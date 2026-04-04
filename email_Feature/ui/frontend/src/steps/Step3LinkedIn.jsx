// src/steps/Step3LinkedIn.jsx

export default function Step3LinkedIn({ data, onChange }) {
  return (
    <div className="space-y-4">
      <div className="bg-amber-50 border border-amber-200 rounded-lg px-4 py-3">
        <p className="text-sm font-medium text-amber-800 mb-1">Optional but recommended</p>
        <p className="text-xs text-amber-700 leading-relaxed">
          Pasting the target person's LinkedIn profile dramatically improves personalization —
          especially for the coffee-chat (team member) email. The AI will reference their
          specific projects, posts, or role to make the email feel genuine rather than templated.
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">
          LinkedIn profile context
        </label>
        <p className="text-xs text-slate-400 mb-2">
          Paste their LinkedIn About section, a recent post they shared, or describe
          what you know about them. No API needed — plain text works perfectly.
        </p>
        <textarea
          className="w-full h-48 px-3 py-2 text-sm border border-slate-200 rounded-lg
                     focus:outline-none focus:ring-2 focus:ring-indigo-400 resize-none
                     bg-white placeholder-slate-300"
          placeholder="Jordan Lee — Staff ML Engineer at Stripe&#10;Currently working on real-time risk scoring infrastructure.&#10;Recently posted about migrating from batch to streaming feature pipelines using Flink..."
          value={data.linkedinPaste}
          onChange={e => onChange({ linkedinPaste: e.target.value })}
        />
        {data.linkedinPaste && (
          <p className="text-xs text-indigo-600 mt-1">
            LinkedIn context will be used to personalize your email.
          </p>
        )}
      </div>

      <button
        className="text-sm text-slate-400 hover:text-slate-600 underline underline-offset-2"
        onClick={() => onChange({ linkedinPaste: '' })}
      >
        Skip this step
      </button>
    </div>
  )
}
