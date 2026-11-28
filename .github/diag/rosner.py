# TEMPORARY diagnostic for PR #79 (removed before merge)
import pandas as pd

import simplydata as sdata
from simplydata._r import r_call

x = [12.1, 14.3, 11.8, 15.2, 13.9, 12.7, 14.8, 13.1, 12.4, 25.6, 3.0, 13.3]
print("before:", list(r_call("search()", _cite=False)))
sdata.table(pd.DataFrame({"v": x})).show_rows_with_outliers("v", test_method="rosner")
print("after rosner:", list(r_call("search()", _cite=False)))
print("predict in:", list(r_call("find('predict')", _cite=False)))
