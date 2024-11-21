import sys
from build_data import get_data

# Global variable to hold filtered counties during runtime
current_data = None


def main():
    # Check if operations file is provided
    if len(sys.argv) != 2:
        print("Error: Please provide a single operations file as a command-line argument.")
        sys.exit(1)

    operations_file = sys.argv[1]

    try:
        with open(operations_file, 'r') as file:
            operations = file.readlines()
    except FileNotFoundError:
        print(f"Error: Unable to open file '{operations_file}'.")
        sys.exit(1)

    # Load full demographics data
    global current_data
    current_data = get_data()
    print(f"Loaded {len(current_data)} county entries.")

    # Process operations
    for line_num, operation in enumerate(operations, start=1):
        operation = operation.strip()
        if not operation:
            continue  # Skip blank lines

        try:
            process_operation(operation)
        except Exception as e:
            print(f"Error: Malformed operation on line {line_num}: '{operation}'")
            print(f"  {e}")


def process_operation(operation):
    """Process a single operation on the county data."""
    global current_data

    if operation == "display":
        display_counties(current_data)
    elif operation.startswith("filter-state:"):
        state = operation.split(":")[1]
        current_data = filter_state(current_data, state)
    elif operation.startswith("filter-gt:"):
        field, value = parse_filter(operation, "filter-gt")
        current_data = filter_gt(current_data, field, float(value))
    elif operation.startswith("filter-lt:"):
        field, value = parse_filter(operation, "filter-lt")
        current_data = filter_lt(current_data, field, float(value))
    elif operation == "population-total":
        print_population_total(current_data)
    elif operation.startswith("population:"):
        field = operation.split(":")[1]
        print_population_subtotal(current_data, field)
    elif operation.startswith("percent:"):
        field = operation.split(":")[1]
        print_population_percentage(current_data, field)
    else:
        raise ValueError(f"Unknown operation: {operation}")


def parse_filter(operation, filter_type):
    """Parse a filter operation into its components."""
    parts = operation.split(":")
    if len(parts) != 3:
        raise ValueError(f"Malformed {filter_type} operation.")
    return parts[1], parts[2]


def display_counties(data):
    """Display the counties in a user-friendly format."""
    for county in data:
        print(f"{county.county}, {county.state} | Population: {county.population['2014 Total Population']}")


def filter_state(data, state):
    """Filter counties by state abbreviation."""
    filtered = [county for county in data if county.state == state]
    print(f"Filter: state == {state} ({len(filtered)} entries)")
    return filtered


def filter_gt(data, field, value):
    """Filter counties where a field is greater than a value."""
    key = field.split(".")
    filtered = [
        county for county in data
        if resolve_field(county, key) > value
    ]
    print(f"Filter: {field} gt {value} ({len(filtered)} entries)")
    return filtered


def filter_lt(data, field, value):
    """Filter counties where a field is less than a value."""
    key = field.split(".")
    filtered = [
        county for county in data
        if resolve_field(county, key) < value
    ]
    print(f"Filter: {field} lt {value} ({len(filtered)} entries)")
    return filtered


def print_population_total(data):
    """Print the total population of the current counties."""
    total_population = sum(county.population['2014 Total Population'] for county in data)
    print(f"2014 population: {total_population}")


def print_population_subtotal(data, field):
    """Print the total population for a sub-population based on a field percentage."""
    key = field.split(".")
    subtotal = sum(
        county.population['2014 Total Population'] * (resolve_field(county, key) / 100)
        for county in data
    )
    print(f"2014 {field} population: {subtotal}")


def print_population_percentage(data, field):
    """Print the percentage of the total population within the specified sub-population."""
    total_population = sum(county.population['2014 Total Population'] for county in data)
    key = field.split(".")
    sub_population = sum(
        county.population['2014 Total Population'] * (resolve_field(county, key) / 100)
        for county in data
    )
    percentage = (sub_population / total_population) * 100 if total_population > 0 else 0
    print(f"2014 {field} percentage: {percentage}")


def resolve_field(county, key):
    """Resolve a hierarchical field name into its value."""
    data = county
    for k in key:
        data = getattr(data, k.lower(), {}).get(k, None) if isinstance(data, dict) else getattr(data, k.lower(), None)
    return data


if __name__ == "__main__":
    main()
