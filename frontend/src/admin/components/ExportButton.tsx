import Button from "@/components/ui/button";
import { toCSV } from "../utils/format";

interface Props<T extends Record<string, any>> {
  data: T[];
  headers: Record<keyof T, string>;
  filename: string;
}

export default function ExportButton<T extends Record<string, any>>({ data, headers, filename }: Props<T>) {
  function handle() {
    const csv = toCSV(data, headers);
    const blob = new Blob([csv], { type: "text/csv" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
  }
  return (
    <Button onClick={handle} className="ml-2">Export CSV</Button>
  );
}
