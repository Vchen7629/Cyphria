from typing import Optional
from src.products.computing.cpu.detector import CPUDetector
from src.products.computing.gpu.detector import GPUDetector
import pytest

cpu_detector = CPUDetector()

@pytest.mark.parametrize(argnames="cpu_names", argvalues=[
    # Ryzen CPUs
    "MAX 395", "MAX+ 395", "Ryzen AI Max 395", "Ryzen AI Max+ 395", "Ryzen AI 9 475", 
    "Ryzen AI 9 HX 475", "Ryzen 3900x3d", "3900x3d", "Ryzen 7 3900x3d", "Ryzen 7 3900", "Ryzen 3 PRO 1300",
    # Threadripper CPUs
    "Threadripper PRO 9995WX", "9995WX", "Threadripper 9980X", "Threadripper 9980X", ""
    # Intel cpus
    "i9-14900", "i9-14900K", "14900K", "265K", "Core Ultra 7 265K", "Core 5 120U", "i7-13700H",
    "13700H", "Pentium G620", "Pentium Gold G620", "G620",])
def test_detects_cpus(cpu_names: str) -> None:
    assert cpu_detector.extract_cpus(cpu_names) == [cpu_names]
    assert cpu_detector.contains_cpu(cpu_names) is True

@pytest.mark.parametrize(argnames="cpu_names", argvalues=[
    "No CPU", None, "", "I just bought the 3900", "I just bought the 9 475"]
)
def test_cpu_invalid_matches(cpu_names: Optional[str]) -> None:
    assert cpu_detector.extract_cpus(cpu_names) == [] # type: ignore
    assert cpu_detector.contains_cpu(cpu_names) is False # type: ignore

@pytest.mark.parametrize(argnames="gpu_sentence,expected", argvalues=[
    ("I just bought the 4090, it's great!", ["4090"]), # bare gpu number 
    ("I just bought the rtx4070ti, it's great!", ["rtx4070ti"]), # no spaces gpu name
    ("Should i buy the rtx 4090 or the rtx5090 for deep learning?", ["rtx 4090", "rtx5090"]), # multiple matches
    ("The 3090 Ti is very good.", ["3090 ti"]), # gpu number with space between suffix 
    ("my 3080fe/7700x starts to crumble on demanding games.", ["3080fe"]), # matches fe
    ("I just bought a 4090 and my friend has a 4090", ["4090"]), # should deduplicate same gpu number
    ("i have a rtx 4090, RTX 3080, and RtX 2070", ["rtx 2070", "rtx 3080", "rtx 4090"]), # case insensitive
    ("I have [RTX 4090], its very nice", ["rtx 4090"]) # should still match with brackets around
])
def test_gpu_valid_matches(gpu_sentence: str, expected: list[str]) -> None:
    """Test if extract gpu function can match valid gpu strings"""
    assert GPUDetector().extract_gpus(gpu_sentence) == expected

@pytest.mark.parametrize(argnames="gpu_sentence", argvalues=[
    "The price is 1234 dollars", "The sushi costs $4090"
])
def test_gpu_invalid_matches(gpu_sentence: str) -> None:
    """Should not match invalid gpu sentences"""
    assert GPUDetector().extract_gpus(gpu_sentence) == []

def test_treats_different_formats_as_different() -> None:
    """Different format should match as different"""
    text = "The RTX 4090 is better than just the 4090"

    result = GPUDetector().extract_gpus(text)

    assert result == ["4090", "rtx 4090"]
