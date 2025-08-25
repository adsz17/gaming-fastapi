export function formatMoney(n: number): string {
  return n.toLocaleString(undefined, { style: "currency", currency: "USD" });
}

export function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString();
}

export function toCSV<T extends Record<string, any>>(rows: T[], headers: Record<keyof T, string>): string {
  const header = Object.keys(headers)
    .map((k) => JSON.stringify(headers[k as keyof T]))
    .join(",");
  const body = rows
    .map((row) =>
      Object.keys(headers)
        .map((k) => JSON.stringify(row[k as keyof T] ?? ""))
        .join(",")
    )
    .join("\n");
  return header + "\n" + body;
}
