import { Rocket, CheckCircle2 } from 'lucide-react'
import { ResetForm } from '@features/auth/ResetForm'

export default function ResetPage() {
  return (
    <div className="min-h-screen flex">
      {/* Left branding panel */}
      <div
        className="hidden lg:flex lg:w-1/2 flex-col justify-center items-center p-12"
        style={{ background: '#0a0f1e' }}
      >
        <div className="max-w-sm w-full">
          <div className="flex items-center gap-3 mb-6">
            <Rocket className="text-sky-400" size={36} />
            <span className="font-sora text-3xl font-bold text-white tracking-tight">
              apply_n_reach
            </span>
          </div>
          <p className="text-slate-300 text-lg mb-10 font-sora">
            Land your next role faster
          </p>
          <ul className="space-y-4">
            {[
              'Track every application in one place',
              'AI-powered resume tailoring per job',
              'Stay on top of deadlines & follow-ups',
            ].map((bullet) => (
              <li key={bullet} className="flex items-start gap-3 text-slate-300 text-sm">
                <CheckCircle2 className="text-sky-400 shrink-0 mt-0.5" size={18} />
                <span>{bullet}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Right form panel */}
      <div className="flex-1 flex items-center justify-center p-8 bg-white">
        <div className="w-full max-w-md">
          <ResetForm />
        </div>
      </div>
    </div>
  )
}
