import type { IServerSideDatasource, IServerSideGetRowsParams } from 'ag-grid-community'

export function useTradesDatasource(): IServerSideDatasource {
  return {
    async getRows(params: IServerSideGetRowsParams) {
      try {
        const res = await fetch('/api/trades/ssrm', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(params.request),
        })
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const { rowData, rowCount } = await res.json()
        params.success({ rowData, rowCount })
      } catch {
        params.fail()
      }
    },
  }
}
