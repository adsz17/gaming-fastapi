import { motion, MotionProps } from "framer-motion";
import { PropsWithChildren } from "react";

export default function FadeIn({ children, ...props }: PropsWithChildren<MotionProps>) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      {...props}
    >
      {children}
    </motion.div>
  );
}
