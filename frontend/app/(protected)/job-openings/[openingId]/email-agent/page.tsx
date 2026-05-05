import EmailAgentPage from '../../../../../src/app/job-tracker/EmailAgentPage'

interface Props {
  params: Promise<{ openingId: string }>
}

export default async function JobOpeningEmailAgentRoutePage({ params }: Props) {
  const { openingId } = await params
  return <EmailAgentPage openingId={openingId} />
}
