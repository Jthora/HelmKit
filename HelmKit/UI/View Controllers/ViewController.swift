  //
//  ViewController.swift
//  HelmKit
//
//  Created by Jordan Trana on 7/13/18.
//  Copyright © 2018 Jordan Trana. All rights reserved.
//

import UIKit
import CoreLocation
import CoreMotion
import SceneKit
import SpriteKit

  class ViewController: UIViewController, UIPickerViewDelegate, UIPickerViewDataSource {

    @IBOutlet weak var planetProgressionPanel: PlanetProgressionPanelView!
    
    @IBOutlet weak var leftPickerView: UIPickerView!
    @IBOutlet weak var leftSubPickerView: UIPickerView!
    @IBOutlet weak var rightPickerView: UIPickerView!
    @IBOutlet weak var rightSubPickerView: UIPickerView!
    
    @IBOutlet weak var topTimeWindowView: UIView!
    @IBOutlet weak var middleTimeWindowView: UIView!
    @IBOutlet weak var bottomTimeWindowView: UIView!
    
    
    @IBOutlet weak var pickerTimeIntervalLabel: UILabel!
    
    @IBOutlet weak var mhdSensorSceneView: SCNView!
    var mhdScene:MHDSensorScene {
        return mhdSensorSceneView.scene as! MHDSensorScene
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        App.state.Restore()
        
        setTimeCycleWindowHighlight(.none)
        
        leftPickerView.dataSource = self
        leftPickerView.delegate = self
        leftSubPickerView.dataSource = self
        leftSubPickerView.delegate = self
        rightPickerView.dataSource = self
        rightPickerView.delegate = self
        rightSubPickerView.dataSource = self
        rightSubPickerView.delegate = self
        
        mhdSensorSceneView.scene = MHDSensorScene.create()
        mhdSensorSceneView.backgroundColor = UIColor.clear
        mhdSensorSceneView.pointOfView = mhdScene.mainCamera
        
        mhdScene.sphere(.smooth).isHidden = false
        mhdScene.sphere(.ripple).isHidden = true
        mhdScene.sphere(.smoothChaos).isHidden = true
        mhdScene.sphere(.rippleChaos).isHidden = true
        mhdScene.sphere(.strongChaos).isHidden = true
    }
    
    var aspectToCalculate:Astrology.Aspect = Astrology.Aspect(primarybody: .mercury, relation: .square, secondaryBody: .jupiter)
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        calculateAspect(aspectToCalculate)
        
        let scaler = App.state.currentScaler
        
        leftPickerView.selectRow(App.state.selectedScalerIndex, inComponent: 0, animated: true)
        leftSubPickerView.selectRow(scaler.unit.rawValue, inComponent: 0, animated: true)
        rightPickerView.selectRow(scaler.scale + 1000000, inComponent: 0, animated: true)
        
        if let index:Int = rightSubPickerCustomContent.firstIndex(where: { $1 == scaler.power } )?.hashValue {
            rightSubPickerView.selectRow(index, inComponent: 0, animated: true)
        } else {
            let index = Int(scaler.power) + rightSubPickerCustomContent.count - 1
            rightSubPickerView.selectRow(index, inComponent: 0, animated: true)
        }
        
        lastSelectedSeconds = timeWindowScale()
        updatePickerTimeIntervalLabel()
        
    }

    func calculateAspect(_ aspect:Astrology.Aspect? = nil) {
        let aspect:Astrology.Aspect = aspect != nil ? aspect! : Astrology.Aspect(primarybody: .sun, relation: .sextile, secondaryBody: .jupiter)
        AstroAngleForeteller.whenIsTheDateOfThisNextAspectAlignment(after: Date(), aspect: aspect, callback: { (date, i) in
            DispatchQueue.main.async {
                let df = DateFormatter()
                df.dateFormat = "y-MM-dd H:m:ss.SSSS"
                let alert = UIAlertController(title: "Completed",
                                              message: "\(df.string(from: date))\n\(i) iterations",
                    preferredStyle: .alert)
                alert.addAction(UIAlertAction(title: "Cancel", style: UIAlertAction.Style.cancel, handler: nil))
                alert.addAction(UIAlertAction(title: "Recalc", style: UIAlertAction.Style.default, handler: { btn in
                    self.calculateAgainButtonTapped(btn)
                }))
                self.show(alert, sender: nil)
            }
        })
    }
    
    @IBAction func calculateAgainButtonTapped(_ sender: Any) {
        calculateAspect(aspectToCalculate)
    }
    
    var lastSelectedSeconds: TimeInterval = 1
    var closestValueConversion:Double {
        
        
        let unitRow = leftSubPickerView.selectedRow(inComponent: 0)
        let multiplierRow = rightSubPickerView.selectedRow(inComponent: 0)
        let valueRow = rightPickerView.selectedRow(inComponent: 0)
        
        guard let unit = Scaler.TimeScaleUnit(rawValue: unitRow)?.seconds else { return 1 }
        let multiplier = Double(leftSubPickerMultipler(row: multiplierRow))
        var value = Double(valueRow - 1000000)
        
        var currentSelectedSeconds = TimeInterval(unit) * (multiplier == 1 ? multiplier * value : pow(multiplier, value))
        
        if multiplier <= 1 || lastSelectedSeconds == currentSelectedSeconds {
            return value
        } else if lastSelectedSeconds > currentSelectedSeconds {
            repeat {
                value += 1
                currentSelectedSeconds = TimeInterval(unit) * (multiplier == 1 ? multiplier * value : pow(multiplier, value))
            } while (lastSelectedSeconds > currentSelectedSeconds)
        } else {
            repeat {
                value -= 1
                currentSelectedSeconds = TimeInterval(unit) * (multiplier == 1 ? multiplier * value : pow(multiplier, value))
            } while (lastSelectedSeconds < currentSelectedSeconds)
        }
        lastSelectedSeconds = currentSelectedSeconds
        return value
    }
    
    func timeWindowScale() ->TimeInterval {
    
        let unitRow = leftSubPickerView.selectedRow(inComponent: 0)
        let multiplierRow = rightSubPickerView.selectedRow(inComponent: 0)
        let valueRow = rightPickerView.selectedRow(inComponent: 0)
        
        guard let unit = Scaler.TimeScaleUnit(rawValue: unitRow)?.seconds else { return 1 }
        let multiplier = Double(leftSubPickerMultipler(row: multiplierRow))
        let value = Double(valueRow - 1000000)
        
        let selectedSeconds = TimeInterval(unit) * (multiplier == 1 ? multiplier * value : pow(multiplier, value))
        
        return selectedSeconds
    }
    
    func updatePickerTimeIntervalLabel() {
        let newSeconds = timeWindowScale()
        pickerTimeIntervalLabel.text = "\(newSeconds == 0 ? "∞" : "\(newSeconds)")"
    }
    
    func storeScalerData() {
        let unitRow = leftSubPickerView.selectedRow(inComponent: 0)
        let powerRow = rightSubPickerView.selectedRow(inComponent: 0)
        let scaleRow = rightPickerView.selectedRow(inComponent: 0)
        
        let power = Double(leftSubPickerMultipler(row: powerRow))
        let scale = Int(scaleRow - 1000000)
        
        App.state.currentScaler.power = power
        App.state.currentScaler.scale = scale
        
        guard let unit = Scaler.TimeScaleUnit(rawValue: unitRow) else { return }
        App.state.currentScaler.unit = unit
        
        App.state.Store()
    }
    
    func leftSubPickerMultipler(row: Int) -> Double {
        if row < rightSubPickerCustomContent.count {
            return Array(rightSubPickerCustomContent.values)[row]
        }
        let multiplier = Double(row + 1 - rightSubPickerCustomContent.count)
        return multiplier
    }
    
    let rightSubPickerCustomContent: [String:Double] = ["e":Constants.e,
                                                       "π":Constants.π]
    
    func pickerView(_ pickerView: UIPickerView, numberOfRowsInComponent component: Int) -> Int {
        if pickerView == leftPickerView {
            return App.state.scalers.count
        } else if pickerView == leftSubPickerView {
            return Scaler.TimeScaleUnit.allCases.count
        } else if pickerView == rightSubPickerView {
            return 1000000 + rightSubPickerCustomContent.count
        } else {
            return 2000000
        }
    }
    
    enum TimeCycleWindowHightlightMode {
        case top
        case middle
        case bottom
        case none
        case all
    }
    func setTimeCycleWindowHighlight(_ mode:TimeCycleWindowHightlightMode) {
        switch mode {
        case .top:
            topTimeWindowView.layer.borderWidth = 1
            middleTimeWindowView.layer.borderWidth = 0
            bottomTimeWindowView.layer.borderWidth = 0
            topTimeWindowView.layer.borderColor = UIColor.white.cgColor
            middleTimeWindowView.layer.borderColor = UIColor.clear.cgColor
            bottomTimeWindowView.layer.borderColor = UIColor.clear.cgColor
        case .middle:
            topTimeWindowView.layer.borderWidth = 0
            middleTimeWindowView.layer.borderWidth = 1
            bottomTimeWindowView.layer.borderWidth = 0
            topTimeWindowView.layer.borderColor = UIColor.clear.cgColor
            middleTimeWindowView.layer.borderColor = UIColor.white.cgColor
            bottomTimeWindowView.layer.borderColor = UIColor.clear.cgColor
        case .bottom:
            topTimeWindowView.layer.borderWidth = 0
            middleTimeWindowView.layer.borderWidth = 0
            bottomTimeWindowView.layer.borderWidth = 1
            topTimeWindowView.layer.borderColor = UIColor.clear.cgColor
            middleTimeWindowView.layer.borderColor = UIColor.clear.cgColor
            bottomTimeWindowView.layer.borderColor = UIColor.white.cgColor
        case .none:
            topTimeWindowView.layer.borderWidth = 0
            middleTimeWindowView.layer.borderWidth = 0
            bottomTimeWindowView.layer.borderWidth = 0
            topTimeWindowView.layer.borderColor = UIColor.clear.cgColor
            middleTimeWindowView.layer.borderColor = UIColor.clear.cgColor
            bottomTimeWindowView.layer.borderColor = UIColor.clear.cgColor
        case .all:
            topTimeWindowView.layer.borderWidth = 1
            middleTimeWindowView.layer.borderWidth = 1
            bottomTimeWindowView.layer.borderWidth = 1
            topTimeWindowView.layer.borderColor = UIColor.white.cgColor
            middleTimeWindowView.layer.borderColor = UIColor.white.cgColor
            bottomTimeWindowView.layer.borderColor = UIColor.white.cgColor
        }
    }
    
    func pickerView(_ pickerView: UIPickerView, didSelectRow row: Int, inComponent component: Int) {
        if pickerView == leftPickerView {
            let scaler = App.state.scalers[row]
            App.state.selectedScalerIndex = row
            switch scaler.name {
            case "Top": setTimeCycleWindowHighlight(.top)
            case "Middle": setTimeCycleWindowHighlight(.middle)
            case "Bottom": setTimeCycleWindowHighlight(.bottom)
            default: setTimeCycleWindowHighlight(.all)
            }
            
            leftSubPickerView.selectRow(scaler.unit.rawValue, inComponent: 0, animated: true)
            rightPickerView.selectRow(scaler.scale + 1000000, inComponent: 0, animated: true)
            
            if let index:Int = rightSubPickerCustomContent.firstIndex(where: { $1 == scaler.power } )?.hashValue {
                rightSubPickerView.selectRow(index, inComponent: 0, animated: true)
            } else {
                let index = Int(scaler.power) + rightSubPickerCustomContent.count - 1
                rightSubPickerView.selectRow(index, inComponent: 0, animated: true)
            }
            
        } else if pickerView == rightSubPickerView {
            rightPickerView.selectRow(Int(closestValueConversion + 1000000), inComponent: 0, animated: true)
        }
        updatePickerTimeIntervalLabel()
        storeScalerData()
    }
    
    func pickerView(_ pickerView: UIPickerView, attributedTitleForRow row: Int, forComponent component: Int) -> NSAttributedString? {
        
        // Setup Style and Attributes
        let style:NSMutableParagraphStyle = NSMutableParagraphStyle()
        style.lineBreakMode = .byClipping
        style.alignment = .left
        var attributes:[NSAttributedString.Key:Any] = [.paragraphStyle : style,
                                                       .backgroundColor : UIColor.white]
        
        // Determine Text
        if pickerView == leftPickerView {
            return NSAttributedString(string: "\(App.state.scalers[row].name)", attributes: attributes)
        } else if pickerView == leftSubPickerView {
            return NSAttributedString(string: "\(Scaler.TimeScaleUnit.allCases[row])                ", attributes: attributes)
        } else if pickerView == rightSubPickerView {
            if row < rightSubPickerCustomContent.count {
                let index = row < rightSubPickerCustomContent.count ? row : 0
                let key = Array(rightSubPickerCustomContent.keys)[index]
                let value = Array(rightSubPickerCustomContent.values)[index]
                attributes += [.foregroundColor : UIColor.green ]
                return NSAttributedString(string: "\(key): \(value)                ", attributes: attributes)
            } else {
                let number = row + 1 - rightSubPickerCustomContent.count
                attributes += [.backgroundColor : number.isPrime ? UIColor.white : UIColor.lightGray,
                               .foregroundColor : number.isPrime ? UIColor.red : UIColor.blue ]
                return NSAttributedString(string: " \(number)                ", attributes: attributes)
            }
        } else if pickerView == rightPickerView {
            let number = row - 1000000
            return NSAttributedString(string: " \(number == 0 ? "∞" : "\(number)")                ", attributes: attributes)
        } else {
            let title:NSAttributedString = NSAttributedString(string: " \(row)                ", attributes: attributes)
            return title
        }
    }
    
    func numberOfComponents(in pickerView: UIPickerView) -> Int {
        return 1
    }
}
