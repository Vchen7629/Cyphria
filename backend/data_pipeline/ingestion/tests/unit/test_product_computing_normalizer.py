from typing import Optional
from src.core.logger import StructuredLogger
from src.products.computing.cpu.normalizer import CPUNameNormalizer
from src.products.computing.gpu.normalizer import GPUNameNormalizer
from src.products.computing.mechanical_keyboard.normalizer import MechanicalKeyboardNormalizer
import pytest


@pytest.mark.parametrize(
    argnames="cpu_names,expected_name",
    argvalues=[
        (["5500X3D", "Ryzen 5500X3D", "Ryzen 5 5500X3D"], "AMD Ryzen 5 5500X3D"),
        (
            ["7995WX", "Ryzen 7995WX", "Ryzen Threadripper Pro 7995WX", "Threadripper Pro 7995WX"],
            "AMD Ryzen Threadripper Pro 7995WX",
        ),
    ],
)
def test_cpu_ryzen_normalized(
    cpu_names: list[str], expected_name: str, mock_logger: StructuredLogger
) -> None:
    """Should normalize ryzen cpus properly"""
    normalizer = CPUNameNormalizer(mock_logger)
    for name in cpu_names:
        assert normalizer.normalize_cpu_list([name]) == [expected_name]


@pytest.mark.parametrize(
    argnames="cpu_names,expected_name",
    argvalues=[
        (["3930K", "Core 3930K", "Core i7-3930K", "i7-3930K"], "Intel Core i7-3930K"),
        (["G5500T", "Pentium G5500T", "Pentium Gold G5500T"], "Intel Pentium Gold G5500T"),
        (["G4900T", "Celeron G4900T"], "Intel Celeron G4900T"),
        (
            [
                "7740X",
                "Core 7740X",
                "i7-7740X",
                "i7 X i7-7740X",
                "Core i7-7740X",
                "Core i7 X i7-7740X",
            ],
            "Intel Core i7 X i7-7740X",
        ),
        (["235T", "Core Ultra 235T", "Core Ultra 5 235T"], "Intel Core Ultra 5 235T"),
    ],
)
def test_cpu_intel_normalized(
    cpu_names: list[str], expected_name: str, mock_logger: StructuredLogger
) -> None:
    """Should normalize intel cpus properly"""
    normalizer = CPUNameNormalizer(mock_logger)
    for name in cpu_names:
        assert normalizer.normalize_cpu_list([name]) == [expected_name]


@pytest.mark.parametrize(
    argnames="cpu_list", argvalues=[None, [], ["Banana", "12345", "idk"], ["9999"]]
)
def test_invalid_cpu_input(cpu_list: Optional[list[str]], mock_logger: StructuredLogger) -> None:
    """CPUNormalizer shouldnt normalize invalid cpu strings"""
    assert CPUNameNormalizer(mock_logger).normalize_cpu_list(cpu_list) == []  # type: ignore


@pytest.mark.parametrize(
    argnames="gpu_list,expected",
    argvalues=[
        (
            ["rtx 4090", "4090"],
            ["NVIDIA RTX 4090"],
        ),  # should deduplicate same gpu with different format
        (
            ["rtx4090", "RtX 4090", "rtx 4090", "4090fe", "  rtx 4090  ", "rtx   4090"],
            ["NVIDIA RTX 4090"],
        ),
    ],
)
def test_gpu_normalized(gpu_list: list[str], expected: list[str]) -> None:
    """GPUs should be properly normalized"""
    assert GPUNameNormalizer().normalize_gpu_list(gpu_list) == expected


@pytest.mark.parametrize(
    argnames="gpu_list", argvalues=[None, [], ["Banana", "12345", "Intel 14700k", "idk"], ["9999"]]
)
def test_invalid_gpu_input(gpu_list: Optional[list[str]]) -> None:
    """GPUNormalizer shouldnt normalize invalid gpu strings"""
    result = GPUNameNormalizer().normalize_gpu_list(gpu_list)  # type: ignore

    assert result == []


def test_mixed_valid_and_invalid() -> None:
    """Valid GPUs should be normalized while invalid ones are filtered out"""
    gpu_list = ["rtx 4090", "Intel 14700k", "7900 xtx", "doggo"]

    result = GPUNameNormalizer().normalize_gpu_list(gpu_list)

    assert result == ["AMD RX 7900 XTX", "NVIDIA RTX 4090"]

@pytest.mark.parametrize(argnames="keyboard_list,expected", argvalues=[
    (["Altair-X", "Vega", "ai03 Vega"], ["ai03 Altair-X", "ai03 Vega"]), # should deduplicate
    (["   Air 01  ", "gEm 01"], ["Akko Air 01", "Akko gEm 01"]), # should handle whitespace + mixed case
    (["jajaja", "Altair-X", "Air 01"], ["ai03 Altair-X", "Akko Air 01"]) # should filter out invalid keyboard
])
def test_valid_mechanical_keyboard(keyboard_list: list[str], expected: list[str]) -> None:
    """Should normalize valid mechanical keyboard names"""
    normalized = sorted(MechanicalKeyboardNormalizer().normalize_keyboard_list(keyboard_list))
    assert normalized == sorted(expected)

@pytest.mark.parametrize(argnames="keyboard_list", argvalues=[None, 123, [123]])
def test_invalid_mechanical_keyboard(keyboard_list: list[str]) -> None:
    """Should just return an empty list for invalid keyboard_list input"""
    assert MechanicalKeyboardNormalizer().normalize_keyboard_list(keyboard_list) == []