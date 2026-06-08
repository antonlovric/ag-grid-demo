<script setup lang="ts">
import { AgGridVue } from 'ag-grid-vue3'
import {
  ModuleRegistry,
  AllCommunityModule,
  themeQuartz,
  type ColDef,
  type ValueFormatterParams,
} from 'ag-grid-community'
import {
  ServerSideRowModelModule,
  RowGroupingModule,
  SetFilterModule,
  FiltersToolPanelModule,
  ColumnsToolPanelModule,
  MenuModule,
} from 'ag-grid-enterprise'
import { useTradesDatasource } from '../composables/useTradesDatasource'

ModuleRegistry.registerModules([
  AllCommunityModule,
  ServerSideRowModelModule,
  RowGroupingModule,
  SetFilterModule,
  FiltersToolPanelModule,
  ColumnsToolPanelModule,
  MenuModule,
])

const datasource = useTradesDatasource()

const usdFormatter = (p: ValueFormatterParams) =>
  p.value != null
    ? p.value.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })
    : ''

const numFormatter = (p: ValueFormatterParams) =>
  p.value != null ? p.value.toLocaleString('en-US', { maximumFractionDigits: 2 }) : ''

const columnDefs: ColDef[] = [
  { field: 'trade_ref', headerName: 'Ref', filter: 'agTextColumnFilter', minWidth: 140 },
  { field: 'trade_date', headerName: 'Date', filter: 'agDateColumnFilter', minWidth: 100 },
  { field: 'direction', headerName: 'Dir', filter: 'agSetColumnFilter', minWidth: 70 },
  { field: 'status', headerName: 'Status', filter: 'agSetColumnFilter', minWidth: 110 },
  { field: 'settlement_status', headerName: 'Settlement', filter: 'agSetColumnFilter', minWidth: 120 },
  {
    field: 'asset_class',
    headerName: 'Asset Class',
    filter: 'agSetColumnFilter',
    enableRowGroup: true,
    minWidth: 120,
  },
  {
    field: 'sector',
    headerName: 'Sector',
    filter: 'agSetColumnFilter',
    enableRowGroup: true,
    minWidth: 120,
  },
  {
    field: 'quantity',
    headerName: 'Qty',
    filter: 'agNumberColumnFilter',
    type: 'numericColumn',
    valueFormatter: numFormatter,
    minWidth: 100,
  },
  {
    field: 'price',
    headerName: 'Price',
    filter: 'agNumberColumnFilter',
    type: 'numericColumn',
    valueFormatter: numFormatter,
    minWidth: 90,
  },
  {
    field: 'notional_usd',
    headerName: 'Notional USD',
    filter: 'agNumberColumnFilter',
    type: 'numericColumn',
    valueFormatter: usdFormatter,
    minWidth: 140,
  },
  { field: 'currency', headerName: 'CCY', filter: 'agTextColumnFilter', minWidth: 65 },
  {
    field: 'pnl_realized',
    headerName: 'PnL Real.',
    filter: 'agNumberColumnFilter',
    type: 'numericColumn',
    valueFormatter: numFormatter,
    minWidth: 110,
  },
  {
    field: 'pnl_unrealized',
    headerName: 'PnL Unreal.',
    filter: 'agNumberColumnFilter',
    type: 'numericColumn',
    valueFormatter: numFormatter,
    minWidth: 120,
  },
]

const defaultColDef: ColDef = {
  sortable: true,
  resizable: true,
  floatingFilter: true,
}
</script>

<template>
  <div class="trades-grid">
    <AgGridVue
      style="height: 100%; width: 100%"
      row-model-type="serverSide"
      :theme="themeQuartz"
      :server-side-datasource="datasource"
      :column-defs="columnDefs"
      :default-col-def="defaultColDef"
      :cache-block-size="100"
      :sidebar="{ toolPanels: ['columns', 'filters'] }"
    />
  </div>
</template>

<style scoped>
.trades-grid {
  height: 100%;
  width: 100%;
}
</style>
