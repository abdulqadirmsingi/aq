import { cn } from "@/lib/utils";

interface LogoProps {
  className?: string;
  accentColor?: string;
}

export function Logo({ className, accentColor = "text-emerald-500" }: LogoProps) {
  return (
    <div className={cn("flex items-center justify-center shrink-0", className)}>
      <svg 
        viewBox="0 0 48 48" 
        fill="none" 
        xmlns="http://www.w3.org/2000/svg" 
        className="w-full h-full"
      >
        {/* A Shape */}
        <path 
          d="M7 37L17 11L27 37" 
          stroke="currentColor" 
          strokeWidth="4" 
          strokeLinejoin="bevel" 
        />
        <path 
          d="M11 27H23" 
          stroke="currentColor" 
          strokeWidth="4" 
        />
        
        {/* Q Shape */}
        <circle 
          cx="29" 
          cy="25" 
          r="10" 
          stroke="currentColor" 
          strokeWidth="4" 
        />
        <path 
          d="M35 31L42 38" 
          className={accentColor}
          stroke="currentColor" 
          strokeWidth="4" 
          strokeLinecap="square" 
        />
        
        {/* Data Node Accent */}
        <circle 
          cx="17" 
          cy="11" 
          r="3" 
          className={accentColor}
          fill="currentColor" 
        />
      </svg>
    </div>
  );
}