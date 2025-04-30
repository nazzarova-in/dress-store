def overlap_date(user_start_date, user_end_date, start_date, end_date):
  return user_start_date > end_date or user_end_date < start_date

# esli periodi ne peresekautsa, funkcia vosvrashaet True

print(overlap_date(1, 10, 11, 50))