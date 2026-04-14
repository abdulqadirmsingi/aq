import Link from "next/link";
import { Logo } from "@/components/ui/logo";

export function Footer() {
  return (
    <footer className="relative bg-white py-20 px-6 text-neutral-900 border-t-2 border-neutral-900 overflow-hidden">
      <div className="relative z-10 mx-auto max-w-7xl">
        <div className="mb-16 grid gap-12 md:grid-cols-2 lg:grid-cols-4">
          <div className="lg:col-span-2">
            <div className="mb-6 flex items-center gap-3">
              <Logo className="h-12 w-12 text-neutral-900" accentColor="text-emerald-500" />
              <span className="text-xl font-bold tracking-widest uppercase">Data Lab</span>
            </div>
            <p className="max-w-md text-base font-medium text-neutral-600 leading-relaxed">
              Transforming complex data into clear, actionable intelligence for Tanzania&apos;s evolving economy.
            </p>
          </div>

          <div>
            <h4 className="mb-6 text-xs font-bold uppercase tracking-widest text-neutral-400">Navigation</h4>
            <ul className="flex flex-col gap-4 text-sm font-bold text-neutral-600">
              <li><Link href="/data" className="hover:text-neutral-900 transition-colors inline-block">Dashboard</Link></li>
              <li><a href="#data" className="hover:text-neutral-900 transition-colors inline-block">Available Data</a></li>
              <li><a href="#roadmap" className="hover:text-neutral-900 transition-colors inline-block">Roadmap</a></li>
            </ul>
          </div>

          <div>
            <h4 className="mb-6 text-xs font-bold uppercase tracking-widest text-neutral-400">Creator</h4>
            <ul className="flex flex-col gap-4 text-sm font-bold text-neutral-600">
              <li>
                <a 
                  href="https://abdulqadirmsingi.com" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="group inline-flex items-center gap-2 hover:text-neutral-900 transition-colors"
                >
                  Abdulqadir Msingi
                  <svg className="h-4 w-4 transition-transform group-hover:-translate-y-0.5 group-hover:translate-x-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="flex flex-col items-center justify-between gap-6 border-t border-neutral-200 pt-8 sm:flex-row text-xs font-bold text-neutral-500">
          <p>
            © {new Date().getFullYear()} AQ Data Lab. All rights reserved.
          </p>
          
          <div className="flex items-center gap-2">
            <span>Designed & Engineered by</span>
            <a 
              href="https://abdulqadirmsingi.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-neutral-900 hover:underline"
            >
              Abdulqadir Msingi
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}