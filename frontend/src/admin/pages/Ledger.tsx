import { useEffect, useState } from "react";
import { ColumnDef } from "@tanstack/react-table";
import { LedgerItem } from "../types";
import { fetchLedger } from "../api";
import { useFilters } from "../filters";
import DataTable from "../components/DataTable";
import Copyable from "../components/Copyable";
import ExportButton from "../components/ExportButton";
import { formatMoney, formatDate } from "../utils/format";
import Badge from "@/components/ui/badge";

export default function Ledger() {
  const { range, userId } = useFilters();
  const [data, setData] = useState<LedgerItem[]>([]);

  useEffect(() => {
    const params: any = {};
    if (range.from) params.from = range.from.toISOString();
    if (range.to) params.to = range.to.toISOString();
    if (userId) params.user_id = userId;
    fetchLedger(params).then(setData);
  }, [range, userId]);

  const columns: ColumnDef<LedgerItem>[] = [
    {
      accessorKey: "id",
      header: "ID",
      cell: (info) => <Copyable value={info.getValue<string>()} />,
    },
    {
      accessorKey: "user_id",
      header: "User",
      cell: (info) => <Copyable value={info.getValue<string>()} />,
    },
    {
      accessorKey: "amount",
      header: "Amount",
      cell: (info) => {
        const v = info.getValue<number>();
        return (
          <Badge className={v >= 0 ? "bg-green-600" : "bg-red-600"}>
            {formatMoney(v)}
          </Badge>
        );
      },
    },
    {
      accessorKey: "balance",
      header: "Balance",
      cell: (info) => formatMoney(info.getValue<number>()),
    },
    {
      accessorKey: "meta",
      header: "Meta",
      cell: (info) => {
        const val = info.getValue<any>();
        const str = typeof val === "string" ? val : JSON.stringify(val);
        return <span title={str}>{str.slice(0, 20)}</span>;
      },
    },
    {
      accessorKey: "created_at",
      header: "Created",
      cell: (info) => formatDate(info.getValue<string>()),
    },
  ];

  return (
    <div>
      <div className="flex justify-end mb-2">
        <ExportButton
          data={data}
          headers={{
            id: "ID",
            user_id: "User",
            amount: "Amount",
            balance: "Balance",
            meta: "Meta",
            created_at: "Created",
          }}
          filename="ledger.csv"
        />
      </div>
      <DataTable data={data} columns={columns} />
    </div>
  );
}
