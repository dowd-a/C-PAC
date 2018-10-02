import numpy as np
from .utils import correlation, p_from_null, phase_randomize


def isfc(D, std=None, collapse_subj=True):

    assert D.ndim == 3

    n_vox, _, n_subj = D.shape
    n_subj_loo = n_subj - 1

    group_sum = np.add.reduce(D, axis=2)

    if collapse_subj:
        ISFC = np.zeros((n_vox, n_vox))
        for loo_subj in range(n_subj):
            ISFC += correlation(
                D[:, :, loo_subj],
                (group_sum - D[:, :, loo_subj]) / n_subj_loo,
                symmetric=True
            )
        ISFC /= n_subj

        if std:
            ISFC_avg = ISFC.mean()
            ISFC_std = ISFC.std()
            masked = (ISFC <= ISFC_avg + ISFC_std) | (ISFC >= ISFC_avg - ISFC_std)
        else:
            masked = np.array([True] * n_vox)

    else:
        ISFC = np.zeros((n_vox, n_vox, n_subj))
        for loo_subj in range(n_subj):
            ISFC[:, :, loo_subj] = correlation(
                D[:, :, loo_subj],
                (group_sum - D[:, :, loo_subj]) / n_subj_loo,
                symmetric=True
            )
        masked = np.array([True] * n_vox)

    return ISFC, masked


def isfc_significance(ISFC, min_null, max_null, two_sided=False):
    p = p_from_null(ISFC,
                    max_null=max_null,
                    min_null=min_null,
                    two_sided=two_sided)
    return p


def isfc_permutation(permutation, D, masked, collapse_subj=True, random_state=0):

    min_null = 1
    max_null = -1

    D = D[masked]

    n_vox, _, n_subj = D.shape
    n_subj_loo = n_subj - 1

    D = phase_randomize(D, random_state)

    if collapse_subj:
        ISFC_null = np.zeros((n_vox, n_vox))

    group_sum = np.add.reduce(D, axis=2)

    for loo_subj in range(n_subj):
        ISFC_subj = \
            correlation(
                D[:, :, loo_subj],
                (group_sum - D[:, :, loo_subj]) / n_subj_loo,
                symmetric=True
            )

        if collapse_subj:
            ISFC_null += ISFC_subj
        else:
            max_null = max(np.max(ISFC_subj), max_null)
            min_null = min(np.min(ISFC_subj), min_null)
    
    if collapse_subj:
        ISFC_null /= n_subj
        max_null = np.max(ISFC_null)
        min_null = np.min(ISFC_null)

    return permutation, min_null, max_null
