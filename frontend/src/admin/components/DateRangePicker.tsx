import { useState } from "react";
import { format } from "date-fns";
import { useFilters, predefinedRange, DateRange } from "../filters";
import { DropdownMenu } from "@/components/ui/dropdown-menu";
import { Dialog } from "@/components/ui/dialog";
import Input from "@/components/ui/input";
import Button from "@/components/ui/button";

export default function DateRangePicker() {
  const { range, setRange } = useFilters();
  const [open, setOpen] = useState(false);
  const [custom, setCustom] = useState<DateRange>({});

  function apply(option: string) {
    setRange(predefinedRange(option));
  }

  function applyCustom() {
    setRange(custom);
    setOpen(false);
  }

  const label = range.from && range.to
    ? `${format(range.from, "yyyy-MM-dd")} → ${format(range.to, "yyyy-MM-dd")}`
    : "Select range";

  return (
    <>
      <DropdownMenu
        label={label}
        options={[
          { label: "Today", onSelect: () => apply("today") },
          { label: "7d", onSelect: () => apply("7d") },
          { label: "30d", onSelect: () => apply("30d") },
          { label: "Custom", onSelect: () => setOpen(true) },
        ]}
      />
      <Dialog open={open} onClose={() => setOpen(false)}>
        <div className="space-y-2">
          <Input
            type="date"
            value={custom.from ? format(custom.from, "yyyy-MM-dd") : ""}
            onChange={(e) => setCustom((c) => ({ ...c, from: new Date(e.target.value) }))}
          />
          <Input
            type="date"
            value={custom.to ? format(custom.to, "yyyy-MM-dd") : ""}
            onChange={(e) => setCustom((c) => ({ ...c, to: new Date(e.target.value) }))}
          />
          <Button className="w-full" onClick={applyCustom}>Apply</Button>
        </div>
      </Dialog>
    </>
  );
}
