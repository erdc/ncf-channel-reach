from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing, QgsProcessingAlgorithm, QgsProcessingParameterFile, QgsProcessingParameterFeatureSource, QgsCoordinateTransform,
                       QgsField, QgsProject, QgsWkbTypes, QgsFields, QgsFeatureRequest, QgsProcessingException, QgsFeature, QgsFeatureSink, NULL,
                       QgsProcessingParameterFeatureSink, QgsProcessingParameterField, QgsJsonUtils, QgsCoordinateTransform)
import csv
import re

class ChannelReachChangelogAlgorithm(QgsProcessingAlgorithm):
    # This is an example algorithm that takes a vector layer, creates some new layers and returns some results.
    
    def tr(self, string):
        # Returns a translatable string with the self.tr() function.
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        # Must return a new copy of your algorithm.
        return ChannelReachChangelogAlgorithm()

    def name(self):
        # Returns the unique algorithm name.
        return 'channelreachchangelog'

    def displayName(self):
        # Returns the translated algorithm name.
        return self.tr('ChannelReach Changelog')

    def group(self):
        # Returns the name of the group this algorithm belongs to.
        return self.tr('ChannelReach')

    def groupId(self):
        # Returns the unique ID of the group this algorithm belongs to.
        return 'channelReach'

    def shortHelpString(self):
        #Returns a localised short help string for the algorithm.
        desc = '''The "ChannelReach Changelog" Processing Algorithm tracks changes between 2 versions of the National Channel Framework ChannelReach polygon layer.
        
        <hr>
        <b>INPUTS</b>
        
        '''
        desc += '• The <b>Old & New ChannelReach layers</b> are your inputs. Accepts polygon vector layers.<br>'
        desc += '• The <b>Old & New ChannelReach IDs</b> are the unique identifier fields based on their respective layer. Usually is named similar to "ChannelReachIDPK".<br>'
        desc += '• The <b>Old & New ChannelReach Fields</b> are all the columns you wish to compare data between. Please keep the order of the columns between layers consistent.'
        desc += '''<hr>
        <b>OUTPUTS</b>
        
        '''
        desc += '• The <b>Tabular Output</b> is the file where the spreadsheet data will be written to. Accepts .csv files.<br>'
        desc += '• The <b>Geospatial Output</b> is a geospatial layer containing records of all ChannelReaches changes, additions, and removals in the new ChannelReach respectively. Accepts polygon vector layers.<br>'
        return self.tr(desc)

    def initAlgorithm(self, config=None):
        # Here we define the inputs and outputs of the algorithm.
        self.addParameter(QgsProcessingParameterFeatureSource('OLD_INPUT', self.tr('Old ChannelReach layer'), types=[QgsProcessing.TypeVectorPolygon]))
        self.addParameter(QgsProcessingParameterField('OLD_IDPK', 'Old ChannelReach ID', type=QgsProcessingParameterField.Any, parentLayerParameterName='OLD_INPUT', allowMultiple=False))
        self.addParameter(QgsProcessingParameterFeatureSource('NEW_INPUT', self.tr('New ChannelReach layer'), types=[QgsProcessing.TypeVectorPolygon]))
        self.addParameter(QgsProcessingParameterField('NEW_IDPK', 'New ChannelReach ID', type=QgsProcessingParameterField.Any, parentLayerParameterName='NEW_INPUT', allowMultiple=False))
        self.addParameter(QgsProcessingParameterField('OLD_FIELDS', 'Old Fields', type=QgsProcessingParameterField.Any, parentLayerParameterName='OLD_INPUT', allowMultiple=True))
        self.addParameter(QgsProcessingParameterField('NEW_FIELDS', 'New Fields', type=QgsProcessingParameterField.Any, parentLayerParameterName='NEW_INPUT', allowMultiple=True))
        self.addParameter(QgsProcessingParameterFile('FILE_OUTPUT', self.tr('Tabular Output'), fileFilter=self.tr('CSV Files (*.csv)')))
        self.addParameter(QgsProcessingParameterFeatureSink('OUTPUT', self.tr('Geospatial Output'), QgsProcessing.TypeVectorPolygon))

    def processAlgorithm(self, parameters, context, feedback):
        # Here is where the processing itself takes place.
        old_layer = self.parameterAsVectorLayer(parameters, 'OLD_INPUT', context)
        if old_layer is None or QgsWkbTypes.geometryType(old_layer.wkbType()) != QgsWkbTypes.PolygonGeometry or old_layer.featureCount() == 0:
            raise QgsProcessingException("Old ChannelReach layer failed to load!")
        old_idpk = self.parameterAsString(parameters, 'OLD_IDPK', context)
        old_fields = self.parameterAsStrings(parameters, 'OLD_FIELDS', context)
        new_layer = self.parameterAsVectorLayer(parameters, 'NEW_INPUT', context)
        if new_layer is None or QgsWkbTypes.geometryType(new_layer.wkbType()) != QgsWkbTypes.PolygonGeometry or new_layer.featureCount() == 0:
            raise QgsProcessingException("New ChannelReach layer failed to load!")
        new_idpk = self.parameterAsString(parameters, 'NEW_IDPK', context)
        new_fields = self.parameterAsStrings(parameters, 'NEW_FIELDS', context)
        output_file = self.parameterAsFile(parameters, 'FILE_OUTPUT', context)
        if len(old_fields) != len(new_fields):
            raise QgsProcessingException("Both Fields parameters must have the same amount of fields!")
        if feedback.isCanceled():
            return {}
        
        def FixDictionary(dict):
            real_dict = eval(re.sub(r"\\/", "/", re.sub(r'\bnull\b', 'None', dict)))
            return real_dict

        tr = QgsCoordinateTransform(old_layer.sourceCrs(), new_layer.sourceCrs(), QgsProject.instance())
        old_layer.startEditing()
        for feat in old_layer.getFeatures():
            feat.geometry().transform(tr)
            old_layer.updateFeature(feat)
        old_layer.commitChanges()

        old_area = {f[old_idpk]: "{:.7f}".format(round(f.geometry().area(), 7)) for f in old_layer.getFeatures()}
        old_dict = {f[old_idpk]: FixDictionary(QgsJsonUtils.exportAttributes(f)) for f in old_layer.getFeatures()}
        new_area = {f[new_idpk]: "{:.7f}".format(round(f.geometry().area(), 7)) for f in new_layer.getFeatures()}
        new_dict = {f[new_idpk]: FixDictionary(QgsJsonUtils.exportAttributes(f)) for f in new_layer.getFeatures()}
        removed_idpk = list(set(old_dict.keys()) - set(new_dict.keys()))
        added_idpk   = list(set(new_dict.keys()) - set(old_dict.keys()))
        changed_idpk = list(set(new_dict.keys()) & set(old_dict.keys()))
        total_percent = 50.0 / (len(new_dict) + len(removed_idpk)) if (len(new_dict) + len(removed_idpk)) else 0
        data = {}
        if feedback.isCanceled():
            return {}
        
        for current, (key, val) in enumerate(new_dict.items()):
            if key in old_dict:
                what_changed = []
                for i in range(len(new_fields)):
                    if old_dict.get(key).get(old_fields[i]) != val.get(new_fields[i]):
                        what_changed.append(new_fields[i])
                if old_area.get(key) != new_area.get(key):
                    what_changed.append('Shape__Area')
                if what_changed != []:
                    final_list = [key, 'Changed ' + ", ".join(what_changed[:-2] + [((len(what_changed) != 2) * ',' + " & ").join(what_changed[-2:])])]
                    for i in range(len(new_fields)):
                        final_list.append(old_dict.get(key).get(old_fields[i]))
                        final_list.append(val.get(new_fields[i]))
                    final_list.extend([old_area.get(key), new_area.get(key)])
                    data.update({key: final_list})
            else:
                final_list = [key, 'Added']
                for name in new_fields:
                    final_list.append(None)
                    final_list.append(val.get(name))
                final_list.extend([None, new_area.get(key)])
                data.update({key: final_list})
            
            feedback.setProgress(int(current * total_percent))
            if feedback.isCanceled():
                return {}
                
        for current, key in enumerate(removed_idpk):
            final_list = [key, 'Removed']
            for name in old_fields:
                final_list.append(old_dict.get(key).get(name))
                final_list.append(None)
            final_list.extend([old_area.get(key), None])
            data.update({key: final_list})
            
            feedback.setProgress(int((len(new_dict) + current) * total_percent))
            if feedback.isCanceled():
                return {}
        
        data = dict(sorted(data.items()))
        created_fields = QgsFields()
        created_fields.append(QgsField('ChannelReachIDPK', QVariant.String))
        created_fields.append(QgsField('Type', QVariant.String))
        for i in range(len(new_fields)):
            created_fields.append(QgsField(f'{old_fields[i]} {old_layer.name()}', QVariant.String))
            created_fields.append(QgsField(f'{new_fields[i]} {new_layer.name()}', QVariant.String))
        created_fields.append(QgsField(f'Shape__Area {old_layer.name()}', QVariant.String))
        created_fields.append(QgsField(f'Shape__Area {new_layer.name()}', QVariant.String))
        if feedback.isCanceled():
            return {}
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(created_fields.names())
            writer.writerows(data.values())
        feedback.setProgress(70)
        if feedback.isCanceled():
            return {}

        created_fields_2 = QgsFields()
        created_fields_2.append(QgsField('ID', QVariant.String))
        created_fields_2.extend(created_fields)
        created_fields_2.append(QgsField('GeometrySource', QVariant.String))
        (sink, dest_id) = self.parameterAsSink(parameters, 'OUTPUT', context, created_fields_2, new_layer.wkbType(), new_layer.sourceCrs())
                
        total_percent = (80.0 - 70.0) / len(removed_idpk) if len(removed_idpk) else 0
        for current, idpk in enumerate(removed_idpk):
            expr = f"{old_idpk} = '{idpk}'"
            for feat in old_layer.getFeatures(QgsFeatureRequest().setFilterExpression(expr)):
                f = QgsFeature()
                f.setGeometry(feat.geometry())
                f.setAttributes([current] + [NULL if d is None else d for d in data.get(idpk)] + ['Old'])
                sink.addFeature(f, QgsFeatureSink.FastInsert)
            
            feedback.setProgress(int(current * total_percent) + 70)
            if feedback.isCanceled():
                return {}
        
        total_percent = (90.0 - 80.0) / len(added_idpk) if len(added_idpk) else 0
        for current, idpk in enumerate(added_idpk):
            expr = f"{new_idpk} = '{idpk}'"
            for feat in new_layer.getFeatures(QgsFeatureRequest().setFilterExpression(expr)):
                f = QgsFeature()
                f.setGeometry(feat.geometry())
                f.setAttributes([len(removed_idpk) + current] + [NULL if d is None else d for d in data.get(idpk)] + ['New'])
                sink.addFeature(f, QgsFeatureSink.FastInsert)
                
            feedback.setProgress(int(current * total_percent) + 80)
            if feedback.isCanceled():
                return {}
        
        total_percent = (100.0 - 90.0) / len(changed_idpk) if len(changed_idpk) else 0
        i = len(removed_idpk) + len(added_idpk)
        changed_idpk = [c for c in changed_idpk if c in data.keys()]
        for current, idpk in enumerate(changed_idpk):
            i += 1
            expr1 = f"{new_idpk} = '{idpk}'"
            for new_feat in new_layer.getFeatures(QgsFeatureRequest().setFilterExpression(expr1)):
                new_f = QgsFeature()
                new_f.setGeometry(new_feat.geometry())
                new_f.setAttributes([i] + [NULL if d is None else d for d in data.get(idpk)] + ['New'])
                sink.addFeature(new_f, QgsFeatureSink.FastInsert)
            
            if data.get(idpk)[-1] != data.get(idpk)[-2]:
                i += 1
                expr2 = f"{old_idpk} = '{idpk}'"
                for old_feat in old_layer.getFeatures(QgsFeatureRequest().setFilterExpression(expr2)):
                    old_f = QgsFeature()
                    old_f.setGeometry(old_feat.geometry())
                    old_f.setAttributes([i] + [NULL if d is None else d for d in data.get(idpk)] + ['Old'])
                    sink.addFeature(old_f, QgsFeatureSink.FastInsert)

            feedback.setProgress(int(current * total_percent) + 90)
            if feedback.isCanceled():
                return {}

        feedback.setProgress(100)
        return {'OUTPUT': dest_id}
