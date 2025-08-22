import Navbar from "@/components/Navbar";
import Card from "@/components/ui/card";
import Button from "@/components/ui/button";
import { Link } from "react-router-dom";

export default function Lobby() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <div className="flex-1 flex items-center justify-center p-4">
        <Card className="max-w-md text-center space-y-4">
          <h1 className="text-3xl font-bold text-neon-pink">Crash Game</h1>
          <p>Bet and watch the multiplier rise. Cash out before it crashes!</p>
          <Link to="/play">
            <Button className="bg-neon-blue">Play Now</Button>
          </Link>
        </Card>
      </div>
    </div>
  );
}
