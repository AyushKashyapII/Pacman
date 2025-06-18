from board import boards

print("Testing board structure:")
print(f"boards type: {type(boards)}")
print(f"boards length: {len(boards)}")

if len(boards) > 0:
    board_data = boards[0]
    print(f"board_data type: {type(board_data)}")
    print(f"board_data length: {len(board_data)}")
    
    if len(board_data) > 0:
        print(f"First row type: {type(board_data[0])}")
        print(f"First row length: {len(board_data[0])}")
        print(f"First row: {board_data[0]}")
        
        # Test accessing a specific cell
        try:
            cell = board_data[0][0]
            print(f"Cell at (0,0): {cell}")
        except Exception as e:
            print(f"Error accessing cell: {e}")
else:
    print("boards is empty") 