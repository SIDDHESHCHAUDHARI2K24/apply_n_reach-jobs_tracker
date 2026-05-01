"""Find job profiles with BOTH personal data AND section data."""
import asyncio
import asyncpg

async def main():
    c = await asyncpg.connect('postgresql://postgres:xyzzyspoon2k01@localhost:5432/fastapi_t2')
    
    # Find JPs with personal data
    rows = await c.fetch("""
        SELECT jp.id, jp.profile_name, jpd.full_name, jpd.email,
               jpd.phone, jpd.location, jpd.linkedin_url, jpd.github_url,
               jpd.portfolio_url, jpd.summary
        FROM job_profiles jp
        JOIN job_profile_personal_details jpd ON jpd.job_profile_id = jp.id
        ORDER BY jp.id DESC LIMIT 10
    """)
    
    for r in rows:
        jp_id = r['id']
        edu = await c.fetchval("SELECT count(*) FROM job_profile_educations WHERE job_profile_id = $1", jp_id)
        exp = await c.fetchval("SELECT count(*) FROM job_profile_experiences WHERE job_profile_id = $1", jp_id)
        proj = await c.fetchval("SELECT count(*) FROM job_profile_projects WHERE job_profile_id = $1", jp_id)
        research = await c.fetchval("SELECT count(*) FROM job_profile_researches WHERE job_profile_id = $1", jp_id)
        cert = await c.fetchval("SELECT count(*) FROM job_profile_certifications WHERE job_profile_id = $1", jp_id)
        skill = await c.fetchval("SELECT count(*) FROM job_profile_skill_items WHERE job_profile_id = $1", jp_id)
        rendered = await c.fetchval("SELECT EXISTS (SELECT 1 FROM rendered_resume WHERE job_profile_id = $1)", jp_id)
        
        total = edu + exp + proj + research + cert + skill
        print(f"JP#{jp_id} | {r['profile_name']} | {r['full_name']} | {r['email']}")
        print(f"  Sections: Edu:{edu} Exp:{exp} Proj:{proj} Res:{research} Cert:{cert} Skill:{skill} | Total:{total} | Rendered:{rendered}")
    
    await c.close()

asyncio.run(main())
