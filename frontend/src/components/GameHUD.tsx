import * as React from "react";

interface GameHUDProps {
  title: string;
  ping: number;
  credits: number;
}

export default function GameHUD({ title, ping, credits }: GameHUDProps) {
  return (
    <div className="flex items-center justify-between p-2 bg-white/60 backdrop-blur-md rounded-2xl shadow-sm">
      <div className="flex items-center gap-2">
        <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-500" />
        <div>
          <h1 className="text-lg font-semibold leading-none">{title}</h1>
          <p className="text-xs text-gray-600">Sector 7 — Online</p>
        </div>
      </div>
      <div className="flex items-center gap-8 text-sm">
        <div className="flex items-center gap-1">
          <span className="text-gray-500">Ping</span>
          <span className="font-medium">{ping}ms</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="text-gray-500">Créditos</span>
          <span className="font-medium">{credits}</span>
        </div>
      </div>
    </div>
  );
}
