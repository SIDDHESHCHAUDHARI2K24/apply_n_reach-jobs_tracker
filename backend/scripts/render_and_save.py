"""Render resume for JP#986 and save PDF to resume/ directory.
Uses backend service functions directly (bypasses auth)."""
import asyncio
import asyncpg
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

async def main():
    conn = await asyncpg.connect('postgresql://postgres:xyzzyspoon2k01@localhost:5432/fastapi_t2')
    
    # Use the service layer directly
    from app.features.job_profile.latex_resume import service
    
    jp_id = 986  # Has 1 item in each of 6 sections
    
    print(f"Rendering resume for JP#{jp_id}...")
    
    # Aggregate data
    profile_data = await service.aggregate_job_profile_data(conn, jp_id)
    personal = profile_data.get('personal', {})
    print(f"  Personal: {personal.get('full_name')} - {personal.get('email')}")
    print(f"  Education: {len(profile_data.get('educations', []))} items")
    print(f"  Experience: {len(profile_data.get('experiences', []))} items")
    print(f"  Projects: {len(profile_data.get('projects', []))} items")
    print(f"  Research: {len(profile_data.get('researches', []))} items")
    print(f"  Certifications: {len(profile_data.get('certifications', []))} items")
    print(f"  Skills: {len(profile_data.get('skill_items', []))} items")
    
    # Render resume (stores in DB + returns metadata)
    from app.features.job_profile.latex_resume.schemas import ResumeLayoutOptions
    layout = ResumeLayoutOptions()
    
    try:
        result = await service.render_resume(conn, jp_id, layout)
        print(f"\nRender successful!")
        print(f"  Template: {result.get('template_name')}")
        print(f"  Rendered at: {result.get('rendered_at')}")
        
        # Get PDF
        pdf_result = await service.get_resume_pdf(conn, jp_id)
        if pdf_result:
            pdf_bytes, filename_stem = pdf_result
            out_dir = Path(r"C:\Projects\FastAPI Tutorial T2\resume")
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{filename_stem}.pdf"
            out_path.write_bytes(pdf_bytes)
            print(f"  PDF saved: {out_path}")
            print(f"  Size: {len(pdf_bytes):,} bytes")
            
            # Also save the LaTeX source for reference
            tex_path = out_dir / f"{filename_stem}.tex"
            tex_path.write_text(profile_data.get('_latex_source', ''), encoding='utf-8')
        else:
            print("  ERROR: Could not retrieve PDF after render")
            
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    await conn.close()

asyncio.run(main())
