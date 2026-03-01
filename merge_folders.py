import shutil
import os

base = r"c:\Users\chakr\Medicine_ERP"
src_data = os.path.join(base, "dist_package", "data")
src_bills = os.path.join(base, "dist_package", "customer_bills")
dst = os.path.join(base, "Gita Medical Hall ERP")

# Copy data
for f in os.listdir(src_data):
    shutil.copy2(os.path.join(src_data, f), os.path.join(dst, "data"))

# Copy bills
for f in os.listdir(src_bills):
    shutil.copy2(os.path.join(src_bills, f), os.path.join(dst, "customer_bills"))

print("Done copying files")
