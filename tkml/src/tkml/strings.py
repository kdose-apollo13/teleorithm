"""
    examples of valid and invalid strings used in properties
"""

valid_strings = [
    "'!some %% wild ** string¡ single quotes'",
    '"!some %% wild ** string¡ double quotes"',
    "'escaped \\\' within single-quoted string'",
    r"'escaped \' within single-quoted raw string'",
    '"escaped \\\" within double-quoted string"',
    r'"escaped \" within double-quoted raw string"',
    "'.special#chars..(ok) ]] `kramerica` [['",
    '".special#chars..(ok) ]] `kramerica` [["',
    """'single-quotes containing "double-quoted" string'""",
    '''"double-quotes containing 'single quoted' string"''',
]

if __name__ == '__main__':
    for s in valid_strings:
        print(s)
