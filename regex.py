from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether occured character is handled by current ctate
        """
        pass

    def check_next(self, next_char: str) -> State | Exception:
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("rejected string")


class StartState(State):
    next_states: list[State] = []

    def __init__(self):
        super().__init__()
        self.next_states = []

    def check_self(self, char):
        return super().check_self(char)


class TerminationState(State):
    def __init__(self):
        super().__init__()
        self.next_states = []

    def check_self(self, char: str) -> bool:
        return False


class DotState(State):
    """
    state for . character (any character accepted)
    """

    next_states: list[State] = []

    def __init__(self):
        super().__init__()
        self.next_states = []

    def check_self(self, char: str):
        return True


class AsciiState(State):
    """
    state for alphabet letters or numbers
    """

    next_states: list[State] = []
    curr_sym = ""

    def __init__(self, symbol: str) -> None:
        super().__init__()
        self.curr_sym = symbol
        self.next_states = []

    def check_self(self, curr_char: str) -> State | Exception:
        return curr_char == self.curr_sym


class StarState(State):

    next_states: list[State] = []

    def __init__(self, checking_state: State):
        super().__init__()
        self.next_states = [checking_state]

    def check_self(self, char):
        for state in self.next_states:
            if state.check_self(char):
                return True

        return False


class PlusState(State):
    next_states: list[State] = []

    def __init__(self, checking_state: State):
        super().__init__()
        self.next_states = [checking_state]

    def check_self(self, char):
        for state in self.next_states:
            if state.check_self(char):
                return True

        return False


class RegexFSM:
    curr_state: State = StartState()

    def __init__(self, regex_expr: str) -> None:
        self.curr_state = StartState()

        prev_state = self.curr_state
        tmp_next_state = self.curr_state

        for char in regex_expr:
            tmp_next_state = self.__init_next_state(char, prev_state, tmp_next_state)
            prev_state.next_states.append(tmp_next_state)

    def __init_next_state(
        self, next_token: str, prev_state: State, tmp_next_state: State
    ) -> State:
        new_state = None

        match next_token:
            case next_token if next_token == ".":
                new_state = DotState()
            case next_token if next_token == "*":
                new_state = StarState(tmp_next_state)
                prev_state.next_states.pop()

            case next_token if next_token == "+":
                new_state = PlusState(tmp_next_state)
                prev_state.next_states.pop()

            case next_token if next_token.isascii():
                new_state = AsciiState(next_token)

            case _:
                raise AttributeError("Character is not supported")

        return new_state

    def check_string(self, s: str) -> bool:
        tokens = self.curr_state.next_states

        def _match(ti: int, si: int) -> bool:
            if ti == len(tokens):
                return si == len(s)

            token = tokens[ti]

            if isinstance(token, StarState):
                if _match(ti + 1, si):
                    return True
                k = si
                while k < len(s) and token.check_self(s[k]):
                    k += 1
                    if _match(ti + 1, k):
                        return True
                return False

            if isinstance(token, PlusState):
                if si >= len(s) or not token.check_self(s[si]):
                    return False
                k = si + 1
                if _match(ti + 1, k):
                    return True
                while k < len(s) and token.check_self(s[k]):
                    k += 1
                    if _match(ti + 1, k):
                        return True
                return False

            if si < len(s) and token.check_self(s[si]):
                return _match(ti + 1, si + 1)
            return False

        return _match(0, 0)


if __name__ == "__main__":
    def expect(pattern: str, text: str, want: bool) -> None:
        got = RegexFSM(pattern).check_string(text)
        status = "OK" if got == want else "FAIL"
        print(f"[{status}] /{pattern}/ on {text!r:>14}  ->  got={got}, want={want}")
        assert got == want

    # from the lab statement
    expect("a*4.+hi", "aaaaaa4uhi", True)
    expect("a*4.+hi", "4uhi",       True)
    expect("a*4.+hi", "meow",       False)

    # letters
    expect("abc", "abc", True)
    expect("abc", "ab",  False)

    # digits with '+'
    expect("1+", "111", True)
    expect("1+", "",    False)
    expect("67", "67",  True)

    # '*' with zero matches
    expect("a*b", "b",    True)
    expect("a*b", "aaab", True)

    print("\nall tests passed.")
