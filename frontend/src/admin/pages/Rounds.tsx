import { useEffect, useState } from "react";
import { ColumnDef } from "@tanstack/react-table";
import { Round } from "../types";
import { fetchRounds } from "../api";
import { useFilters } from "../filters";
import DataTable from "../components/DataTable";
import Copyable from "../components/Copyable";
import ExportButton from "../components/ExportButton";
import { formatMoney, formatDate } from "../utils/format";

export default function Rounds() {
  const { range, userId } = useFilters();
  const [data, setData] = useState<Round[]>([]);

  useEffect(() => {
    const params: any = { order: "created_at.desc" };
    if (range.from) params.from = range.from.toISOString();
    if (range.to) params.to = range.to.toISOString();
    if (userId) params.user_id = userId;
    fetchRounds(params).then(setData);
  }, [range, userId]);

  const columns: ColumnDef<Round>[] = [
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
      accessorKey: "bet",
      header: "Bet",
      cell: (info) => formatMoney(info.getValue<number>()),
    },
    {
      accessorKey: "payout",
      header: "Payout",
      cell: (info) => formatMoney(info.getValue<number>()),
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
            bet: "Bet",
            payout: "Payout",
            created_at: "Created",
          }}
          filename="rounds.csv"
        />
      </div>
      <DataTable data={data} columns={columns} />
    </div>
  );
}
