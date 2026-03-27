# Architect PoC - Lessons Learned

## HTTP Redirect Handling
**Issue:** During the initial batch tests, the `docs.xandr.com` URL returned a `301 MOVED PERMANENTLY` redirect because Microsoft moved the documentation to `learn.microsoft.com`. The default behavior of the `httpx` client is to reject redirects, which threw a `PIPELINE EXCEPTION` and halted the processing of that integration.

**Resolution:** 
While failing on redirects safely prevents the system from processing empty HTTP bodies or malicious redirect chains, in the ad-tech integration context, documentation is frequently reorganized and moved. We updated the extraction script to explicitly include `follow_redirects=True` in `httpx` to allow the Architect to seamlessly follow standard 301/302 redirects to the new documentation homes.
