import Link from "next/link";

export function Hero() {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center bg-neutral-50 text-neutral-900 px-6 pt-20">
      {/* Refined Grid Background */}
      <div className="absolute inset-0 z-0 pointer-events-none opacity-20" 
           style={{ backgroundImage: "linear-gradient(to right, #171717 1px, transparent 1px), linear-gradient(to bottom, #171717 1px, transparent 1px)", backgroundSize: "4rem 4rem" }} 
      />

      <div className="relative z-10 flex max-w-5xl flex-col items-center text-center">
        <h1 className="mb-8 text-4xl font-black tracking-tighter sm:text-8xl lg:text-9xl uppercase leading-[0.95] text-neutral-900">
          <span className="block">
            Uncover
          </span>
          <span className="block text-white" style={{ textShadow: "2px 2px 0 #171717, -1px -1px 0 #171717, 1px -1px 0 #171717, -1px 1px 0 #171717, 1px 1px 0 #171717" }}>
            The Truth.
          </span>
        </h1>

        <p className="mb-12 max-w-3xl text-xl sm:text-2xl font-medium leading-relaxed text-neutral-600">
          A multi-sector view of Tanzania&apos;s historical records, current signals, and decision-ready intelligence. 
          We transform raw numbers into <span className="font-bold text-neutral-900">actionable insights</span>.
        </p>

        <div className="flex flex-col gap-4 sm:flex-row">
          <Link 
            href="/data" 
            className="group relative inline-flex h-14 items-center justify-center gap-3 border-2 border-neutral-900 bg-neutral-900 px-10 font-bold uppercase tracking-widest text-white shadow-[4px_4px_0px_0px_rgba(0,0,0,0.2)] transition-all hover:bg-neutral-800 hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none"
          >
            <span>Explore Data</span>
            <svg className="h-5 w-5 transition-transform group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </Link>
          <a 
            href="#data" 
            className="inline-flex h-14 items-center justify-center border-2 border-neutral-900 bg-white px-10 font-bold uppercase tracking-widest text-neutral-900 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-all hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none"
          >
            Learn More
          </a>
        </div>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-10 left-1/2 -translate-x-1/2 animate-bounce border-2 border-neutral-900 bg-white p-2 shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
        <svg className="h-5 w-5 text-neutral-900" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
        </svg>
      </div>
    </section>
  );
}