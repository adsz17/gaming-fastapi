import * as React from "react";
import GameHUD from "@/components/GameHUD";
import GameActionBar from "@/components/GameActionBar";

export default function UIDemo() {
  const handleSubmit = (value: string) => {
    console.log("Comando:", value);
  };

  return (
    <div className="min-h-screen flex flex-col gap-8 p-4 font-inter">
      <GameHUD title="Galaxy Run" ping={18} credits={1200} />
      <div className="flex-1 flex items-center justify-center rounded-2xl bg-gray-100 shadow-inner">
        Aquí va la escena del juego
      </div>
      <GameActionBar onSubmit={handleSubmit} />
    </div>
  );
}
