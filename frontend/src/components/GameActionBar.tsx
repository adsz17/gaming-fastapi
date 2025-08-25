import * as React from "react";
import GameActionButton from "@/components/GameActionButton";

interface GameActionBarProps {
  onSubmit: (value: string) => void;
}

export default function GameActionBar({ onSubmit }: GameActionBarProps) {
  const [value, setValue] = React.useState("");

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!value.trim()) return;
    onSubmit(value);
    setValue("");
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex items-center gap-2 p-2 bg-white/60 backdrop-blur-md rounded-2xl shadow-sm"
    >
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Comando / destino / acción…"
        className="flex-1 bg-transparent px-4 py-2 text-gray-900 placeholder-gray-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 rounded-2xl"
      />
      <GameActionButton aria-label="Enviar comando" type="submit" />
    </form>
  );
}
