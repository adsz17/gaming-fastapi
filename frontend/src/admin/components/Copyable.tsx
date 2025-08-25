import { useToast } from "@/components/ui/toast";

export default function Copyable({ value }: { value: string }) {
  const toast = useToast();
  return (
    <span
      onClick={() => {
        navigator.clipboard.writeText(value);
        toast("Copied");
      }}
      className="cursor-pointer underline decoration-dotted"
    >
      {value}
    </span>
  );
}
