"""Find job profiles with populated sections and rendered resumes."""
import asyncio
import asyncpg

async def main():
    c = await asyncpg.connect('postgresql://postgres:xyzzyspoon2k01@localhost:5432/fastapi_t2')
    
    # Find JP IDs with rendered resumes
    rendered = await c.fetch("SELECT job_profile_id, template_name, rendered_at, octet_length(pdf_content) as size FROM rendered_resume ORDER BY rendered_at DESC")
    
    print(f"Total rendered resumes: {len(rendered)}")
    
    for r in rendered:
        jp_id = r['job_profile_id']
        
        # Count data in each section
        edu = await c.fetchval("SELECT count(*) FROM job_profile_educations WHERE job_profile_id = $1", jp_id)
        exp = await c.fetchval("SELECT count(*) FROM job_profile_experiences WHERE job_profile_id = $1", jp_id)
        proj = await c.fetchval("SELECT count(*) FROM job_profile_projects WHERE job_profile_id = $1", jp_id)
        res = await c.fetchval("SELECT count(*) FROM job_profile_researches WHERE job_profile_id = $1", jp_id)
        cert = await c.fetchval("SELECT count(*) FROM job_profile_certifications WHERE job_profile_id = $1", jp_id)
        skill = await c.fetchval("SELECT count(*) FROM job_profile_skill_items WHERE job_profile_id = $1", jp_id)
        
        # Get personal info
        pers = await c.fetchrow("SELECT full_name, email, phone, location FROM job_profile_personal_details WHERE job_profile_id = $1", jp_id)
        
        total = edu + exp + proj + res + cert + skill
        
        print(f"\nJP#{jp_id} | {r['rendered_at']} | {r['size']:,} bytes | total items: {total}")
        print(f"  Personal: {dict(pers) if pers else 'NONE'}")
        print(f"  Education: {edu} | Experience: {exp} | Projects: {proj} | Research: {res} | Certs: {cert} | Skills: {skill}")
        
        if total > 0:
            print(f"  *** HAS DATA ***")
    
    await c.close()

asyncio.run(main())
