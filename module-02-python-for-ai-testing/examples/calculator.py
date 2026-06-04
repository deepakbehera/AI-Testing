add = lambda x,y: x+y
subtract = lambda x,y: x-y
multiply = lambda x,y: x*y
divide = lambda x,y: x/y
square = lambda x: x*x
square_root = lambda x: x**0.5
cube = lambda x: x**3
cube_root = lambda x: x**(1/3)

if __name__ == "__main__":
    print("Testing the calculator functions:")
    print(f"5 + 3 = {add(5, 3)}")
    print(f"5 - 3 = {subtract(5, 3)}")
    print(f"5 * 3 = {multiply(5, 3)}")
    print(f"5 / 3 = {divide(5, 3)}")
    print(f"Square of 4 = {square(4)}")
    print(f"Square root of 16 = {square_root(16)}")
    print(f"Cube of 2 = {cube(2)}")
    print(f"Cube root of 27 = {cube_root(27)}")