from __future__ import division, absolute_import
from builtins import str
from builtins import object
from xarray import Dataset, DataArray
import warnings

axis_types = ['lev', 'lat', 'lon', 'depth', 'abstract']


def Field_to_xarray(field):
    '''Convert a climlab.Field object to xarray.DataArray'''
    dom = field.domain
    dims = []; dimlist = []; coords = {};
    for axname in dom.grid.axes:
        if axname not in axis_types:
            dimname = 'abstract'
        else:
            dimname = axname
        dimlist.append(axname)
        try:
            assert field.interfaces[dom.axis_index[axname]]
            bounds_name = dimname + '_bounds'
            dims.append(bounds_name)
            coords[bounds_name] = dom.axes[bounds_name]
        except:
            dims.append(dimname)
            coords[dimname] = dom.axes[dimname]
    #  Might need to reorder the data
    da = DataArray(field.transpose([dom.axis_index[name] for name in dimlist]),
                      dims=dims, coords=coords)
    for name in dims:
        try:
            da[name].attrs['units'] = dom.axes[name].attrs['units']
        except:
            pass
    return da

def state_to_xarray(state):
    '''Convert a dictionary of climlab.Field objects to xarray.Dataset

    Input: dictionary of climlab.Field objects
    (e.g. process.state or process.diagnostics dictionary)

    Output: xarray.Dataset object with all spatial axes,
    including 'bounds' axes indicating cell boundaries in each spatial dimension.

    Any items in the dictionary that are not instances of climlab.Field
    are ignored.'''
    from climlab.domain.field import Field

    ds = Dataset()
    for name, field in state.items():
        if isinstance(field, Field):
            ds[name] = Field_to_xarray(field)
            dom = field.domain
            for axname, ax in dom.axes.items():
                if axname not in axis_types:
                    dimname = 'abstract'
                else:
                    dimname = axname
                bounds_name = dimname + '_bounds'
                ds.coords[bounds_name] = DataArray(ax[bounds_name], dims=[bounds_name],
                                    coords={bounds_name:ax[bounds_name]})
                try:
                    ds[bounds_name].attrs['units'] = ax.units
                except:
                    pass
        else:
            warnings.warn('{} excluded from Dataset because it is not a Field variable.'.format(name))
    return ds

def to_xarray(input):
    '''Convert climlab input to xarray format.

    If input is a climlab.Field object, return xarray.DataArray

    If input is a dictionary (e.g. process.state or process.diagnostics),
    return xarray.Dataset object with all spatial axes,
    including 'bounds' axes indicating cell boundaries in each spatial dimension.

    Any items in the dictionary that are not instances of climlab.Field
    are ignored.'''
    from climlab.domain.field import Field
    if isinstance(input, Field):
        return Field_to_xarray(input)
    elif isinstance(input, dict):
        return state_to_xarray(input)
    else:
        raise TypeError('input must be Field object or dictionary of Field objects')
