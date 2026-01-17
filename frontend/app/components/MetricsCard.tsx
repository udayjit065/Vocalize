
"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface MetricsCardProps {
  label: string;
  value: string | number;
  unit?: string;
  icon?: React.ReactNode;
  delay?: number;
  loading?: boolean;
}

export function MetricsCard({
  label,
  value,
  unit,
  icon,
  delay = 0,
  loading = false,
}: MetricsCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      className={cn(
        "relative overflow-hidden rounded-lg border border-black/10 bg-white p-6 transition-all hover:bg-gray-50",
        loading && "animate-pulse"
      )}
    >
      <div className="flex items-center justify-between mb-4">
        <span className="text-[10px] font-bold uppercase tracking-[0.1em] text-black/40">
          {label}
        </span>
        {icon && <div className="text-black/20">{icon}</div>}
      </div>
      
      <div className="flex items-baseline gap-1.5">
        <span className="text-3xl font-semibold tracking-tight text-black">
          {loading ? "---" : value}
        </span>
        {unit && !loading && (
          <span className="text-[10px] font-bold text-black/30 tracking-wide uppercase">
            {unit}
          </span>
        )}
      </div>
    </motion.div>
  );
}