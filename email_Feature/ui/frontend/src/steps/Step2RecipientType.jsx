// src/steps/Step2RecipientType.jsx

const TYPES = [
  {
    id: 'recruiter',
    label: 'Recruiter',
    description: 'Concise, conversion-focused. Highlights your top 2–3 matching skills with a clear call to action.',
    tag: '150–200 words',
  },
  {
    id: 'team_member',
    label: 'Team member',
    description: 'Warm coffee-chat request. References their work and asks for a 20-min conversation — no mention of job applications.',
    tag: '120–180 words',
  },
  {
    id: 'hiring_manager',
    label: 'Hiring manager',
    description: 'Confident and outcome-oriented. Connects your achievements directly to what the team needs based on the job description.',
    tag: '180–220 words',
  },
]

export default function Step2RecipientType({ data, onChange }) {
  return (
    <div className="space-y-3">
      <p className="text-sm text-slate-500">
        Choose who you want to reach out to. Each type generates a different email
        with a tone and structure suited to that recipient.
      </p>
      {TYPES.map(type => (
        <button
          key={type.id}
          onClick={() => onChange({ recipientType: type.id })}
          className={`w-full text-left px-4 py-4 rounded-xl border-2 transition-all
            ${data.recipientType === type.id
              ? 'border-indigo-500 bg-indigo-50'
              : 'border-slate-200 bg-white hover:border-slate-300'
            }`}
        >
          <div className="flex items-center justify-between mb-1">
            <span className="font-medium text-slate-800">{type.label}</span>
            <span className="text-xs text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
              {type.tag}
            </span>
          </div>
          <p className="text-sm text-slate-500 leading-relaxed">{type.description}</p>
        </button>
      ))}
    </div>
  )
}
