import hashlib
import random
import time


async def generate_md5_hash(text):
    md5 = hashlib.md5()
    md5.update(text.encode('utf-8'))
    return md5.hexdigest()


async def generate_referral_hash():
    fixed_referral_string = "fixed_referral_string"
    random_seed = str(time.time()) + str(random.randint(1, 1000))
    referral_code = fixed_referral_string + random_seed
    referral_hash = await generate_md5_hash(referral_code)
    return referral_hash
