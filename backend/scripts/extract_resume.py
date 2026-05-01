"""Extract rendered resume PDF from DB and save to resume/ directory."""
import asyncio
import asyncpg
from pathlib import Path

async def main():
    c = await asyncpg.connect('postgresql://postgres:xyzzyspoon2k01@localhost:5432/fastapi_t2')
    
    # Get latest resume render (JP#52)
    row = await c.fetchrow("""
        SELECT r.pdf_content, r.template_name, r.rendered_at, r.job_profile_id,
               jp.profile_name, jpd.full_name
        FROM rendered_resume r
        JOIN job_profiles jp ON jp.id = r.job_profile_id
        LEFT JOIN job_profile_personal_details jpd ON jpd.job_profile_id = r.job_profile_id
        ORDER BY r.rendered_at DESC LIMIT 1
    """)
    
    if not row:
        print("No rendered resume found!")
        return
    
    pdf_bytes = row['pdf_content']
    profile_name = row['profile_name']
    full_name = row.get('full_name', '') or ''
    jp_id = row['job_profile_id']
    
    # Build filename
    name_parts = full_name.strip().split()
    if len(name_parts) >= 2:
        first, last = name_parts[0], name_parts[-1]
    elif name_parts:
        first, last = name_parts[0], ''
    else:
        first, last = 'resume', ''
    
    stem = f"{first}_{last}_{profile_name}".replace(' ', '_').lower()
    stem = ''.join(c if c.isalnum() or c in '-_' else '_' for c in stem)
    
    # Save to resume/ directory
    out_dir = Path(r"C:\Projects\FastAPI Tutorial T2\resume")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{stem}.pdf"
    
    out_path.write_bytes(pdf_bytes)
    
    print(f"Saved resume PDF:")
    print(f"  Job Profile: #{jp_id} ({profile_name})")
    print(f"  Name: {full_name}")
    print(f"  Rendered: {row['rendered_at']}")
    print(f"  Size: {len(pdf_bytes):,} bytes")
    print(f"  Output: {out_path}")
    
    # Also show which sections have data
    sections = {}
    for label, tbl in [
        ('Education', 'job_profile_educations'),
        ('Experience', 'job_profile_experiences'),
        ('Projects', 'job_profile_projects'),
        ('Research', 'job_profile_researches'),
        ('Certifications', 'job_profile_certifications'),
        ('Skills', 'job_profile_skill_items'),
    ]:
        count = await c.fetchval(f"SELECT count(*) FROM {tbl} WHERE job_profile_id = $1", jp_id)
        sections[label] = count
    
    print(f"  Sections: {sections}")
    
    await c.close()

asyncio.run(main())
