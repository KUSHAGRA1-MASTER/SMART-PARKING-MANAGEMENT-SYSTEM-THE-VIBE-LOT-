# Set the number of rows
n = 5

# Outer loop for rows
for i in range(n):
    # Inner loop for columns (prints letters from 'a' up to current row)
    for j in range(i + 1):
        # 97 is the ASCII value for lowercase 'a'
        print(chr(97 + j), end="")
    # Move to the next line after each row
    print()
