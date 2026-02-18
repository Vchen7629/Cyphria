from typing import Optional
from src.products.computing.cpu.detector import CPUDetector
import pytest

cpu_detector = CPUDetector()

@pytest.mark.parametrize(argnames="cpu_names", argvalues=[
    # Ryzen CPUs
    "MAX 395", "MAX+ 395", "Ryzen AI Max 395", "Ryzen AI Max+ 395", "Ryzen AI 9 475", 
    "Ryzen AI 9 HX 475", "Ryzen 3900x3d", "3900x3d", "Ryzen 7 3900x3d", "Ryzen 7 3900",
    # Threadripper CPUs
    "Ryzen Threadripper PRO 9995WX", "Threadripper PRO 9995WX", "PRO 9995WX",
    "Ryzen 9995WX", "9995WX", "Ryzen Threadripper 9980X", "Threadripper 9980X", "9980X",
    # Epyc CPUs
    "Epyc 9004", "Epyc 9004F", "9004F",
    # Intel cpus
    "i9-14900", "i9-14900K", "14900K", "265K", "Ultra 7 265K", "Core 5 120U", "i7-13700H", "13700H",
    "Xeon 676", "Xeon w9-3595", "w9-3595X", "Xeon w-1390", "W-1390P", "Xeon e-2488", "E-2488G", "676x"])
def test_detects_cpus(cpu_names: str) -> None:
    assert cpu_detector.extract_cpus(cpu_names) == [cpu_names]
    assert cpu_detector.contains_cpu(cpu_names) is True

@pytest.mark.parametrize(argnames="cpu_names", argvalues=[
    "No CPU", None, "", "I just bought the 3900", "I just bought the 9 475"]
)
def test_invalid_matches(cpu_names: Optional[str]) -> None:
    assert cpu_detector.extract_cpus(cpu_names) == [] # type: ignore
    assert cpu_detector.contains_cpu(cpu_names) is False # type: ignore
