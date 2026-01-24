import pandas as pd

facts = pd.read_csv('output/facts/facts.csv', low_memory=False)

print('✓ SCHEMA EXPANSION COMPLETE\n')
print('=' * 80)
print(f'Schema size: {len(facts.columns)-1} fields (was 32, now {len(facts.columns)-1})')
print(f'Total records: {len(facts):,}')

print(f'\n✓ NEW FIELDS NOW BEING EXTRACTED:\n')
print('  Health/Medical:')
print(f'    • microchipped: {facts["microchipped"].notna().sum():,} ({facts["microchipped"].notna().mean()*100:.1f}%)')
print(f'    • vaccinated: {facts["vaccinated"].notna().sum():,} ({facts["vaccinated"].notna().mean()*100:.1f}%)')
print(f'    • health_checked: {facts["health_checked"].notna().sum():,} ({facts["health_checked"].notna().mean()*100:.1f}%)')
print(f'    • health_tested: {facts["health_tested"].notna().sum():,} ({facts["health_tested"].notna().mean()*100:.1f}%)')
print(f'    • vet_checked: {facts["vet_checked"].notna().sum():,} ({facts["vet_checked"].notna().mean()*100:.1f}%)')
print(f'    • wormed: {facts["wormed"].notna().sum():,} ({facts["wormed"].notna().mean()*100:.1f}%)')
print(f'    • flea_treated: {facts["flea_treated"].notna().sum():,} ({facts["flea_treated"].notna().mean()*100:.1f}%)')

print('\n  Breeding/Lineage:')
print(f'    • sire: {facts["sire"].notna().sum():,} ({facts["sire"].notna().mean()*100:.1f}%)')
print(f'    • dam: {facts["dam"].notna().sum():,} ({facts["dam"].notna().mean()*100:.1f}%)')
print(f'    • sire_health_tested: {facts["sire_health_tested"].notna().sum():,} ({facts["sire_health_tested"].notna().mean()*100:.1f}%)')
print(f'    • dam_health_tested: {facts["dam_health_tested"].notna().sum():,} ({facts["dam_health_tested"].notna().mean()*100:.1f}%)')
print(f'    • champion_bloodline: {facts["champion_bloodline"].notna().sum():,} ({facts["champion_bloodline"].notna().mean()*100:.1f}%)')
print(f'    • pedigree: {facts["pedigree"].notna().sum():,} ({facts["pedigree"].notna().mean()*100:.1f}%)')
print(f'    • dna_tested: {facts["dna_tested"].notna().sum():,} ({facts["dna_tested"].notna().mean()*100:.1f}%)')

print('\n  Dog Attributes:')
print(f'    • sex: {facts["sex"].notna().sum():,} ({facts["sex"].notna().mean()*100:.1f}%)')
print(f'    • color: {facts["color"].notna().sum():,} ({facts["color"].notna().mean()*100:.1f}%)')
print(f'    • age: {facts["age"].notna().sum():,} ({facts["age"].notna().mean()*100:.1f}%)')

print('\n  Breeder Credibility:')
print(f'    • breeder_verified: {facts["breeder_verified"].notna().sum():,} ({facts["breeder_verified"].notna().mean()*100:.1f}%)')
print(f'    • five_star_breeder: {facts["five_star_breeder"].notna().sum():,} ({facts["five_star_breeder"].notna().mean()*100:.1f}%)')
print(f'    • assured_breeder: {facts["assured_breeder"].notna().sum():,} ({facts["assured_breeder"].notna().mean()*100:.1f}%)')
print(f'    • licensed_breeder: {facts["licensed_breeder"].notna().sum():,} ({facts["licensed_breeder"].notna().mean()*100:.1f}%)')

print('\n  Other:')
print(f'    • home_reared: {facts["home_reared"].notna().sum():,} ({facts["home_reared"].notna().mean()*100:.1f}%)')
print(f'    • family_reared: {facts["family_reared"].notna().sum():,} ({facts["family_reared"].notna().mean()*100:.1f}%)')
print(f'    • delivery_available: {facts["delivery_available"].notna().sum():,} ({facts["delivery_available"].notna().mean()*100:.1f}%)')
print(f'    • puppy_contract: {facts["puppy_contract"].notna().sum():,} ({facts["puppy_contract"].notna().mean()*100:.1f}%)')
print(f'    • insurance_available: {facts["insurance_available"].notna().sum():,} ({facts["insurance_available"].notna().mean()*100:.1f}%)')
print(f'    • kc_registered: {facts["kc_registered"].notna().sum():,} ({facts["kc_registered"].notna().mean()*100:.1f}%)')
print(f'    • ad_id: {facts["ad_id"].notna().sum():,} ({facts["ad_id"].notna().mean()*100:.1f}%)')

print('\n' + '=' * 80)
print('\nBREAKDOWN BY PLATFORM (New Fields Added)\n')

for platform in ['pets4homes', 'gumtree', 'freeads', 'kennel_club', 'champdogs', 'preloved', 'foreverpuppy', 'puppies', 'petify']:
    pdata = facts[facts['platform'] == platform]
    if len(pdata) == 0:
        continue
    
    # Count how many new health fields this platform now has
    new_health_fields = ['sex', 'color', 'age', 'microchipped', 'vaccinated', 'wormed', 'flea_treated', 
                         'health_checked', 'vet_checked', 'health_tested', 'kc_registered',
                         'sire', 'dam', 'sire_health_tested', 'dam_health_tested', 'champion_bloodline',
                         'pedigree', 'dna_tested', 'home_reared', 'family_reared', 'breeder_verified',
                         'five_star_breeder', 'assured_breeder', 'licensed_breeder',
                         'delivery_available', 'puppy_contract', 'insurance_available', 'ad_id']
    
    fields_with_data = [f for f in new_health_fields if pdata[f].notna().sum() > 0]
    
    print(f"{platform.ljust(15)} - {len(fields_with_data)}/{len(new_health_fields)} new fields populated")
    if fields_with_data:
        print(f"    {', '.join(fields_with_data[:5])}", end='')
        if len(fields_with_data) > 5:
            print(f", ... and {len(fields_with_data)-5} more")
        else:
            print()

print('\n' + '=' * 80)
