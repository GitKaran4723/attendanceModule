
from app import app, db
from models import Section, Program

def fix_sections():
    with app.app_context():
        print("Checking for sections with NULL program_id...")
        
        # Find sections with null program_id
        bad_sections = Section.query.filter(Section.program_id == None).all()
        
        if not bad_sections:
            print("✅ No sections with NULL program_id found.")
            return

        print(f"⚠️ Found {len(bad_sections)} sections with NULL program_id.")
        
        # Get a default program (e.g. BCA)
        default_program = Program.query.first()
        if not default_program:
            print("❌ No programs found! Cannot fix sections.")
            return
            
        print(f"Using default program: {default_program.name} ({default_program.program_id})")
        
        for section in bad_sections:
            print(f"  - Fixing section: {section.section_name} (ID: {section.section_id})")
            section.program_id = default_program.program_id
            
        try:
            db.session.commit()
            print("✅ All sections fixed successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error committing changes: {e}")

if __name__ == '__main__':
    fix_sections()
