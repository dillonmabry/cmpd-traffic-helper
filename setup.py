from setuptools import setup

setup(name='charlotte_traffic_analysis',
      version='0.1.2',
      description='Charlotte-metro traffic analysis helper including predictions, travel paths, and more',
      author='Dillon Mabry',
      author_email='rapid.dev.solutions@gmail.com',
      license='MIT',
      packages=['cmpd_accidents', 'traffic_analyzer'],
      test_suite='nose.collector',
      tests_require=['nose'],
      install_requires=['pymongo', 'requests', 'lxml', 'bs4', 'sqlalchemy',
                        'pymysql', 'numpy', 'pandas', 'scikit-learn', 'xgboost',
                        'shapely', 'matplotlib'],
      include_package_data=True,
      data_files=[('', [
          'cmpd_accidents/resources/soap_descriptors/cmpd_soap_descriptor.xml',
          'cmpd_accidents/resources/db/mysql_create_accidents.sql',
          'traffic_analyzer/resources/reference_data/census_income.csv',
          'traffic_analyzer/resources/reference_data/census_population.csv',
          'traffic_analyzer/resources/reference_data/roads.csv',
          'traffic_analyzer/resources/reference_data/signals.csv',
          'traffic_analyzer/resources/reference_data/traffic_volumes.csv',
          'traffic_analyzer/resources/models/xgb_cv_optimal.joblib'
      ])],
      zip_safe=False)
