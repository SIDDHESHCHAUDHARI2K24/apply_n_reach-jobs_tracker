import { redirect } from 'next/navigation'

interface PageProps {
  params: Promise<{ openingId: string }>
}

export default async function OpeningResumeIndexPage({ params }: PageProps) {
  const { openingId } = await params
  redirect(`/job-openings/${openingId}/resume/personal`)
}
