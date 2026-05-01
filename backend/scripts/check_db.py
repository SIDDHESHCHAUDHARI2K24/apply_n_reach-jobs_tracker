"""Quick DB check script."""
import asyncio
import asyncpg

async def main():
    c = await asyncpg.connect('postgresql://postgres:xyzzyspoon2k01@localhost:5432/fastapi_t2')
    
    # Check rendered_resume table
    exists = await c.fetchval("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'rendered_resume')")
    print(f"rendered_resume table exists: {exists}")
    
    if exists:
        rows = await c.fetch("SELECT job_profile_id, template_name, rendered_at, octet_length(pdf_content) as size FROM rendered_resume ORDER BY rendered_at DESC LIMIT 5")
        print(f"Resume renders: {len(rows)}")
        for r in rows:
            print(f"  JP#{r['job_profile_id']} | {r['template_name']} | {r['rendered_at']} | {r['size']} bytes")
    
    # Check job profiles
    jp_rows = await c.fetch("SELECT id, profile_name, status, created_at FROM job_profiles ORDER BY id DESC LIMIT 5")
    print(f"\nJob profiles: {len(jp_rows)}")
    for r in jp_rows:
        print(f"  #{r['id']} | {r['profile_name']} | {r['status']} | {r['created_at']}")
    
    # Check if users exist
    user_count = await c.fetchval("SELECT count(*) FROM users")
    print(f"\nUsers: {user_count}")
    if user_count > 0:
        users = await c.fetch("SELECT id, email, created_at FROM users LIMIT 3")
        for u in users:
            print(f"  #{u['id']} | {u['email']}")
    
    await c.close()

asyncio.run(main())
