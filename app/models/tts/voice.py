from enum import Enum


class Voice(Enum):
    def __new__(cls, value: str):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.id = len(cls.__members__)
        return obj

    # English
    AFHeart = "af_heart"
    AFAlloy = "af_alloy"
    AFAoede = "af_aoede"
    AFBella = "af_bella"
    AFJessica = "af_jessica"
    AFKore = "af_kore"
    AFNicole = "af_nicole"
    AFNova = "af_nova"
    AFRiver = "af_river"
    AFSarah = "af_sarah"
    AFSky = "af_sky"
    AMAdam = "am_adam"
    AMEcho = "am_echo"
    AMEric = "am_eric"
    AMFenrir = "am_fenrir"
    AMLiam = "am_liam"
    AMMichael = "am_michael"
    AMOnyx = "am_onyx"
    AMPuck = "am_puck"
    AMSanta = "am_santa"
    BFAlice = "bf_alice"
    BFEmma = "bf_emma"
    BFIsabella = "bf_isabella"
    BFLily = "bf_lily"
    BMDaniel = "bm_daniel"
    BMFable = "bm_fable"
    BMGeorge = "bm_george"
    BMLewis = "bm_lewis"

    # Spanish
    EFDora = "ef_dora"
    EMAlex = "em_alex"
    EMSanta = "em_santa"

    # French
    FFSiwis = "ff_siwis"

    # Italian
    IFSara = "if_sara"
    IMNicola = "im_nicola"

    # Brazilian Portuguese
    PFDora = "pf_dora"
    PMAlex = "pm_alex"
    PMSanta = "pm_santa"

    @classmethod
    def from_id(cls, id_: int) -> "Voice":
        for member in cls:
            if member.id == id_:
                return member
        raise ValueError(f"No Voice with id={id_}")

    @classmethod
    def from_value(cls, value: str) -> "Voice":
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"No Voice with value='{value}'")
