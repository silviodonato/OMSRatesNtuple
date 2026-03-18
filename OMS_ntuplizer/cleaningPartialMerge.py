#!/usr/bin/env python3
import os
import glob
import shutil

def clean_and_organize():
    # Grab all .root files in the current directory
    files = glob.glob("*.root")
    
    if not files:
        print("No .root files found.")
        return

    # Group files by category (e.g., 'circulating', 'physics')
    categories = {}
    for f in files:
        parts = f.split('_')
        if len(parts) >= 2:
            category = parts[0]
            if category not in categories:
                categories[category] = []
            categories[category].append(f)

    print("=== Execution Plan ===")
    
    for category, file_list in categories.items():
        # 1. Identify all partialMerged files for this category
        pm_files = [f for f in file_list if "partialMerged" in f]
        
        if not pm_files:
            continue
            
        # 2. Find the single largest partialMerged file by exact byte size
        largest_pm = max(pm_files, key=lambda f: os.path.getsize(f))
        
        # Extract the run number from the largest partialMerged file
        try:
            largest_num = int(largest_pm.split('_')[1])
        except (IndexError, ValueError):
            print(f"[{category}] Error parsing run number from {largest_pm}. Skipping.")
            continue
            
        print(f"\n[{category}] KEEP (Largest Merged): {largest_pm} (Run: {largest_num})")
        
        # 3. Evaluate all other files in this category
        for f in file_list:
            if f == largest_pm:
                continue
                
            # Extract the run number for the current file
            try:
                # This safely extracts the number from both formats: 
                # "circulating_402062.root" and "circulating_402045_partialMerged.root"
                f_num = int(f.split('_')[1].split('.')[0])
            except (IndexError, ValueError):
                continue
            
            tobefixed = False
            # TASK A: Clean up the partialMerge (Delete all other partialMerged files)
            if "partialMerged" in f:
                print(f"  -> DELETE:       {f}")
                os.remove(f)
            
            # TASK B: Move files with a number above the largest partialMerged
            elif f_num > largest_num:
                print(f"  -> MOVE TO '..': {f}")
                tobefixed = True
                shutil.move(f, "..")
                
            # Ignore standard .root files that are older/smaller than the largest merged
            else:
                pass
#                print(f"  -> IGNORE:       {f}")
        if tobefixed:
                cleanOldPartialMerged = f"../{category}_*_partialMerged.root"
                print(f"  -> DELETE {cleanOldPartialMerged} (... move to /tmp)")
                try:
                    shutil.move(cleanOldPartialMerged, "/tmp")
                except:
                    pass
                cleanOldFullMerge = f"../../{category}_merged.root"
                print(f"  -> DELETE {cleanOldFullMerge} (... move to /tmp)")
                try:
                    shutil.move(cleanOldFullMerge, "/tmp")
                except:
                    pass
                print(f"  -> COPY TO '..': {largest_pm}")
                shutil.copy(largest_pm, "..")

if __name__ == "__main__":
    clean_and_organize()
