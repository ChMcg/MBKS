

class FdGenerator():
    counter = 0
    descriptors: dict[int, str] = {}
    
    @staticmethod
    def new_fd() -> int:
        FdGenerator.counter += 1
        return FdGenerator.counter
    
    def new_file(path: str) -> int:
        fd = FdGenerator.new_fd()
        FdGenerator.descriptors[fd] = path
        return fd
