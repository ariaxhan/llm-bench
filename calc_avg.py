def calc_avg(lst):
    """
    Calculate the average of numeric values in a list, ignoring non-numeric values.

    Args:
        lst: A list that may contain numbers and non-numeric values

    Returns:
        float: The average of numeric values, or 0.0 if no numeric values exist
    """
    if not lst:
        return 0.0

    total = 0
    count = 0

    for item in lst:
        if isinstance(item, (int, float)):
            total += item
            count += 1

    return total / count if count > 0 else 0.0


# Test the function with the provided example
if __name__ == "__main__":
    result = calc_avg([1, 2, 3, "x", 4])
    print(f"calc_avg([1, 2, 3, 'x', 4]) = {result}")  # Should print 2.5

    # Additional test cases
    print(f"calc_avg([]) = {calc_avg([])}")  # Should print 0.0
    print(f"calc_avg(['a', 'b', 'c']) = {calc_avg(['a', 'b', 'c'])}")  # Should print 0.0
    print(f"calc_avg([10, 20, 30]) = {calc_avg([10, 20, 30])}")  # Should print 20.0
    print(
        f"calc_avg([1.5, 2.5, 'hello', 3]) = {calc_avg([1.5, 2.5, 'hello', 3])}"
    )  # Should print 2.333...
