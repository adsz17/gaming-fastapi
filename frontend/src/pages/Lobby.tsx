import Navbar from "@/components/Navbar";
import Button from "@/components/ui/button";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";

export default function Lobby() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <div className="flex-1 relative">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage:
              "url('https://images.unsplash.com/photo-1526772662000-d968d6e3a65e?auto=format&fit=crop&w=1400&q=80')",
          }}
        />
        <div className="relative z-10 flex flex-col items-center justify-center h-full bg-black/60 text-center p-4">
          <motion.h1
            className="text-4xl font-bold text-white mb-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            Crash Game
          </motion.h1>
          <motion.p
            className="mb-6 max-w-md text-white"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            Bet and watch the multiplier rise. Cash out before it crashes!
          </motion.p>
          <Link to="/play">
            <Button className="bg-neon-blue">Play Now</Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
