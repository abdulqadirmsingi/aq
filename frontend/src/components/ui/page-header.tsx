import { cn } from "@/lib/utils";

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  className?: string;
  children?: React.ReactNode;
}

export function PageHeader({ title, subtitle, className, children }: PageHeaderProps) {
  return (
    <div className={cn(
      "relative mb-8 overflow-hidden rounded-[2rem] bg-gradient-to-br from-indigo-900 via-slate-900 to-violet-950 p-8 text-white shadow-2xl transition-all duration-500 sm:p-12",
      className
    )}>
      {/* Decorative background elements */}
      <div className="absolute -right-20 -top-20 h-72 w-72 rounded-full bg-indigo-500/20 blur-[100px]" />
      <div className="absolute -bottom-32 -left-20 h-96 w-96 rounded-full bg-violet-600/20 blur-[120px]" />
      
      <div className="relative z-10 flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
        <div>
          <div className="mb-4 flex items-center gap-2">
            <span className="relative flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500"></span>
            </span>
            <span className="text-xs font-bold tracking-widest text-emerald-400 uppercase">Live Data</span>
          </div>
          <h1 className="text-4xl font-extrabold tracking-tight text-white sm:text-5xl lg:text-6xl">{title}</h1>
          {subtitle && <p className="mt-4 max-w-2xl text-lg text-indigo-200/80 leading-relaxed font-light">{subtitle}</p>}
        </div>
        {children && <div className="mt-6 md:mt-0">{children}</div>}
      </div>
    </div>
  );
}
